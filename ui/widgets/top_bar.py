from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class TopBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("TopBar")
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)

        # Кнопка открытия/скрытия ростера контактов
        self.menu_button = QPushButton("☰")
        self.menu_button.setFixedSize(32, 28)
        self.menu_button.setToolTip("Показать / скрыть список контактов")

        # Аватар активного контакта
        self.avatar_label = QLabel("🌸")
        self.avatar_label.setObjectName("TopAvatar")
        self.avatar_label.setFixedSize(32, 32)
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Имя, UIN и статусная строка
        info_col = QVBoxLayout()
        info_col.setContentsMargins(0, 0, 0, 0)
        info_col.setSpacing(1)

        self.contact_name = QLabel("Лиза")
        self.contact_name.setObjectName("TopContactName")

        self.contact_note = QLabel("UIN: 194-820-771")
        self.contact_note.setObjectName("TopContactNote")

        info_col.addWidget(self.contact_name)
        info_col.addWidget(self.contact_note)

        # Статус
        self.status = QLabel("● Online")
        self.status.setObjectName("TopStatus")
        self.status.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Кнопки действий
        self.new_contact_button = QPushButton("+ Контакт")
        self.new_contact_button.setToolTip("Создать нового ИИ-собеседника")

        self.clear_chat_button = QPushButton("Очистить")
        self.clear_chat_button.setToolTip("Очистить историю переписки с этим контактом")

        self.settings_button = QPushButton("⚙ Настройки")
        self.settings_button.setToolTip("Темы оформления и настройки ИИ")

        layout.addWidget(self.menu_button)
        layout.addWidget(self.avatar_label)
        layout.addLayout(info_col)
        layout.addStretch()
        layout.addWidget(self.status)
        layout.addWidget(self.new_contact_button)
        layout.addWidget(self.clear_chat_button)
        layout.addWidget(self.settings_button)
