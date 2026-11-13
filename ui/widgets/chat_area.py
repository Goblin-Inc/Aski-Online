from typing import List
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from backend.database.models import Contact, Message
from .contact_item import ContactItemWidget
from .message_widget import MessageFormatter
from .typing_widget import TypingWidget


class ChatArea(QWidget):
    contactSelected = Signal(int)  # contact_id

    def __init__(self):
        super().__init__()
        self.setObjectName("ChatArea")
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Список контактов (ростер)
        self.contacts = QListWidget()
        self.contacts.setObjectName("ContactList")
        self.contacts.setFixedWidth(240)
        self.contacts.itemClicked.connect(self._on_item_clicked)

        # Правая часть: область сообщений + индикатор набора
        right_col = QVBoxLayout()
        right_col.setContentsMargins(0, 0, 0, 0)
        right_col.setSpacing(4)

        self.chat = QTextEdit()
        self.chat.setObjectName("ChatHistory")
        self.chat.setReadOnly(True)

        self.typing_widget = TypingWidget()

        right_col.addWidget(self.chat, 1)
        right_col.addWidget(self.typing_widget)

        layout.addWidget(self.contacts)
        layout.addLayout(right_col, 1)

    def populate_contacts(self, contacts: List[Contact], active_id: int):
        self.contacts.clear()
        selected_row = 0
        for idx, c in enumerate(contacts):
            item = QListWidgetItem(self.contacts)
            item.setData(Qt.ItemDataRole.UserRole, c.id)
            item.setSizeHint(QSize(225, 52))
            widget = ContactItemWidget(c)
            self.contacts.setItemWidget(item, widget)
            if c.id == active_id:
                selected_row = idx

        if contacts:
            self.contacts.setCurrentRow(selected_row)

    def _on_item_clicked(self, item: QListWidgetItem):
        cid = item.data(Qt.ItemDataRole.UserRole)
        if cid is not None:
            self.contactSelected.emit(int(cid))

    def render_messages(self, messages: List[Message]):
        self.chat.clear()
        html_blocks = [MessageFormatter.format_message_html(m) for m in messages]
        self.chat.setHtml("".join(html_blocks))
        self.scroll_to_bottom()

    def append_message(self, msg: Message):
        cursor = self.chat.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(MessageFormatter.format_message_html(msg))
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        sb = self.chat.verticalScrollBar()
        sb.setValue(sb.maximum())
