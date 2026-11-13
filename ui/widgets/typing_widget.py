from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget


class TypingWidget(QWidget):
    """Анимированный индикатор набора сообщения («Лиза печатает...»)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TypingWidget")
        self._contact_name = "Собеседник"
        self._dots = 0

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 2, 10, 2)

        self.label = QLabel("")
        self.label.setObjectName("TypingLabel")
        layout.addWidget(self.label)
        layout.addStretch()

        self.timer = QTimer(self)
        self.timer.setInterval(380)
        self.timer.timeout.connect(self._tick)
        self.hide()

    def start_typing(self, contact_name: str):
        self._contact_name = contact_name
        self._dots = 1
        self._update_text()
        self.show()
        self.timer.start()

    def stop_typing(self):
        self.timer.stop()
        self.hide()

    def _tick(self):
        self._dots = (self._dots % 3) + 1
        self._update_text()

    def _update_text(self):
        dots_str = "." * self._dots
        self.label.setText(f"✎ {self._contact_name} печатает сообщение{dots_str}")
