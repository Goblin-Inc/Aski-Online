from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from backend.database.database import db
from backend.database.models import Contact


class CreateContactDialog(QDialog):
    contactCreated = Signal(Contact)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить новый ИИ-контакт")
        self.resize(460, 420)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: Кира // Киберпанк-дизайнер")

        self.avatar_combo = QComboBox()
        self.avatar_combo.addItems(["❀", "🌸", "💀", "⚡", "🏛️", "🤖", "🦊", "🎸", "🌙", "🔥"])

        self.status_combo = QComboBox()
        self.status_combo.addItems(["● Online", "● Free for Chat", "● Away", "● N/A", "● Occupied"])

        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("Короткая подпись статуса (например: В сети 24/7)")

        self.persona_input = QTextEdit()
        self.persona_input.setPlaceholderText(
            "Опишите характер, манеру речи, интересы и биографию персонажа..."
        )
        self.persona_input.setFixedHeight(110)

        self.greeting_input = QLineEdit()
        self.greeting_input.setPlaceholderText("Первое приветственное сообщение в чате...")

        form.addRow("Имя контакта:", self.name_input)
        form.addRow("Иконка / Аватар:", self.avatar_combo)
        form.addRow("Статус в сети:", self.status_combo)
        form.addRow("Статусная строка:", self.note_input)
        form.addRow("Характер (Промпт):", self.persona_input)
        form.addRow("Приветствие:", self.greeting_input)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Добавить в список")
        save_btn.clicked.connect(self._on_save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _on_save(self):
        name = self.name_input.text().strip()
        persona = self.persona_input.toPlainText().strip()
        if not name or not persona:
            QMessageBox.warning(
                self,
                "Заполните поля",
                "Укажите имя персонажа и описание его характера (промпт).",
            )
            return

        contact = db.create_contact(
            name=name,
            avatar=self.avatar_combo.currentText(),
            status=self.status_combo.currentText(),
            status_note=self.note_input.text().strip() or "В сети Aski Online",
            persona=persona,
            greeting=self.greeting_input.text().strip() or f"Привет! Я {name}. Рад знакомству в Aski!",
        )
        self.contactCreated.emit(contact)
        self.accept()
