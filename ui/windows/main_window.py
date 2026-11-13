from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from app.config import config
from app.constants import AI_PROVIDERS, STYLES_DIR
from backend.ai.provider import ai_worker
from backend.database.database import db
from backend.database.models import Contact
from ui.widgets.chat_area import ChatArea
from ui.widgets.chat_input import ChatInput
from ui.widgets.status_bar import StatusBar
from ui.widgets.top_bar import TopBar
from ui.windows.create_contact import CreateContactDialog
from ui.windows.settings_window import SettingsWindow


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aski Online — Retro AI Messenger")
        self.resize(940, 660)
        self.setMinimumSize(720, 500)
        self.setWindowFlag(Qt.WindowType.Window)

        self.active_contact: Optional[Contact] = None

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(8)

        self.top_bar = TopBar()
        self.chat_area = ChatArea()
        self.chat_input = ChatInput()
        self.status_bar = StatusBar()

        self.main_layout.addWidget(self.top_bar)
        self.main_layout.addWidget(self.chat_area, 1)
        self.main_layout.addWidget(self.chat_input)
        self.main_layout.addWidget(self.status_bar)

        self._connect_signals()
        self.apply_theme()
        self._update_provider_status()
        self._load_initial_state()

    def _connect_signals(self):
        self.top_bar.menu_button.clicked.connect(self.toggle_contacts_panel)
        self.top_bar.new_contact_button.clicked.connect(self.open_create_contact_dialog)
        self.top_bar.clear_chat_button.clicked.connect(self.clear_current_chat)
        self.top_bar.settings_button.clicked.connect(self.open_settings_dialog)

        self.chat_area.contactSelected.connect(self.select_contact)
        self.chat_input.send_button.clicked.connect(self.send_user_message)

    def _load_initial_state(self):
        show_panel = bool(config.get("show_contacts_panel", True))
        self.chat_area.contacts.setVisible(show_panel)

        contacts = db.get_contacts()
        saved_id = int(config.get("active_contact_id", 1))
        target_id = saved_id if any(c.id == saved_id for c in contacts) else (contacts[0].id if contacts else 1)

        self.chat_area.populate_contacts(contacts, target_id)
        if contacts:
            self.select_contact(target_id)

    def toggle_contacts_panel(self):
        visible = not self.chat_area.contacts.isVisible()
        self.chat_area.contacts.setVisible(visible)
        config.set("show_contacts_panel", visible)

    def select_contact(self, contact_id: int):
        contact = db.get_contact(contact_id)
        if not contact:
            return
        self.active_contact = contact
        config.set("active_contact_id", contact.id)

        self.top_bar.avatar_label.setText(contact.avatar or "❀")
        self.top_bar.contact_name.setText(contact.name)
        self.top_bar.contact_note.setText(f"UIN {contact.uin}  •  {contact.status_note}")
        self.top_bar.status.setText(contact.status)

        messages = db.get_messages(contact.id, limit=120)
        self.chat_area.render_messages(messages)
        self.chat_input.input.setFocus()

    def send_user_message(self):
        if not self.active_contact:
            return
        text = self.chat_input.input.text().strip()
        if not text:
            return

        self.chat_input.input.clear()
        user_nick = config.get("user_nickname", "Denegen")

        user_msg = db.add_message(self.active_contact.id, "user", user_nick, text)
        self.chat_area.append_message(user_msg)

        # Обновляем превью в списке контактов
        self.chat_area.populate_contacts(db.get_contacts(), self.active_contact.id)

        # Запускаем генерацию ответа ИИ в фоне
        self.chat_area.typing_widget.start_typing(self.active_contact.name)
        self.status_bar.status.setText(f"❀ Передача пакета для {self.active_contact.name} ({self.active_contact.uin})...")

        ai_worker.request_reply(
            self.active_contact,
            text,
            on_finished=self._on_ai_reply_received,
            on_error=self._on_ai_reply_error,
        )

    def _on_ai_reply_received(self, contact_id: int, reply_text: str):
        self.chat_area.typing_widget.stop_typing()
        contact = db.get_contact(contact_id)
        if not contact:
            return

        ai_msg = db.add_message(contact.id, "ai", contact.name, reply_text)
        if self.active_contact and self.active_contact.id == contact.id:
            self.chat_area.append_message(ai_msg)
            QApplication.beep()

        self.chat_area.populate_contacts(
            db.get_contacts(),
            self.active_contact.id if self.active_contact else contact.id,
        )
        self.status_bar.status.setText(f"❀ Сообщение от {contact.name} получено")

    def _on_ai_reply_error(self, _contact_id: int, error_msg: str):
        self.chat_area.typing_widget.stop_typing()
        self.status_bar.status.setText(f"⚠ Ошибка сети: {error_msg}")

    def open_create_contact_dialog(self):
        dlg = CreateContactDialog(self)
        dlg.contactCreated.connect(self._on_contact_created)
        dlg.exec()

    def _on_contact_created(self, new_contact: Contact):
        contacts = db.get_contacts()
        self.chat_area.populate_contacts(contacts, new_contact.id)
        self.select_contact(new_contact.id)
        self.status_bar.status.setText(f"❀ Контакт {new_contact.name} ({new_contact.uin}) добавлен в ростер")

    def clear_current_chat(self):
        if not self.active_contact:
            return
        ans = QMessageBox.question(
            self,
            "Очистить историю",
            f"Удалить всю переписку с контактом «{self.active_contact.name}»?",
        )
        if ans == QMessageBox.StandardButton.Yes:
            db.clear_messages(self.active_contact.id)
            self.chat_area.render_messages([])
            self.chat_area.populate_contacts(db.get_contacts(), self.active_contact.id)
            self.status_bar.status.setText("❀ История переписки очищена")

    def open_settings_dialog(self):
        dlg = SettingsWindow(self)
        dlg.settingsChanged.connect(self._on_settings_updated)
        dlg.exec()

    def _on_settings_updated(self):
        self.apply_theme()
        self._update_provider_status()
        self.status_bar.status.setText("❀ Настройки сохранены и применены")

    def _update_provider_status(self):
        prov_key = config.get("ai_provider", "free_cloud")
        prov_label = AI_PROVIDERS.get(prov_key, prov_key)
        self.status_bar.provider_label.setText(f"AI: {prov_label}")

    def apply_theme(self):
        theme_key = config.get("theme", "classic")
        qss_file = STYLES_DIR / f"{theme_key}.qss"
        if not qss_file.exists():
            qss_file = STYLES_DIR / "classic.qss"
        if qss_file.exists():
            app = QApplication.instance()
            if app:
                app.setStyleSheet(qss_file.read_text(encoding="utf-8"))
