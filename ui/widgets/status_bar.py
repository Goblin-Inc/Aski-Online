from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget


class StatusBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("StatusBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 3, 8, 3)

        self.status = QLabel("❀ Connected to Aski Network")
        self.status.setObjectName("StatusText")

        self.provider_label = QLabel("AI: Aski Free Cloud")
        self.provider_label.setObjectName("StatusProvider")

        layout.addWidget(self.status)
        layout.addStretch()
        layout.addWidget(self.provider_label)
