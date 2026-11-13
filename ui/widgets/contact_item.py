from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from backend.database.models import Contact


class ContactItemWidget(QWidget):
    """Виджет контакта в ростере Aski Online с аватаркой, UIN, статусом и превью."""

    def __init__(self, contact: Contact, parent=None):
        super().__init__(parent)
        self.contact = contact
        self.setObjectName("ContactItem")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        self.avatar_label = QLabel(contact.avatar or "❀")
        self.avatar_label.setObjectName("ContactAvatar")
        self.avatar_label.setFixedSize(34, 34)
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(4)

        self.name_label = QLabel(contact.name)
        self.name_label.setObjectName("ContactName")

        is_online = "Online" in (contact.status or "")
        dot_color = "#22c55e" if is_online else "#f59e0b"
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet(f"color: {dot_color}; font-size: 10px;")

        top_row.addWidget(self.status_dot)
        top_row.addWidget(self.name_label, 1)

        preview_text = (contact.last_message_preview or contact.status_note or f"UIN {contact.uin}").strip()
        if len(preview_text) > 30:
            preview_text = preview_text[:28] + "…"
        self.note_label = QLabel(preview_text)
        self.note_label.setObjectName("ContactNote")

        info_layout.addLayout(top_row)
        info_layout.addWidget(self.note_label)

        layout.addWidget(self.avatar_label)
        layout.addLayout(info_layout, 1)
