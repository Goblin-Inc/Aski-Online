from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QWidget


class ChatInput(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("ChatInput")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)

        self.input = QLineEdit()
        self.input.setObjectName("MessageInput")
        self.input.setPlaceholderText("Напишите сообщение и нажмите Enter...")

        self.send_button = QPushButton("Отправить ↵")
        self.send_button.setObjectName("SendButton")

        layout.addWidget(self.input, 1)
        layout.addWidget(self.send_button)

        self.input.returnPressed.connect(self.send_button.click)
