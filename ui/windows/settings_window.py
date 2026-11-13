from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from app.config import config
from app.constants import AI_PROVIDERS, THEMES


class SettingsWindow(QDialog):
    settingsChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки Aski Online")
        self.resize(460, 360)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        self.nick_input = QLineEdit(config.get("user_nickname", "Denegen"))

        self.theme_combo = QComboBox()
        for key, label in THEMES.items():
            self.theme_combo.addItem(label, key)
        cur_theme_idx = self.theme_combo.findData(config.get("theme", "classic"))
        if cur_theme_idx >= 0:
            self.theme_combo.setCurrentIndex(cur_theme_idx)

        self.provider_combo = QComboBox()
        for key, label in AI_PROVIDERS.items():
            self.provider_combo.addItem(label, key)
        cur_prov_idx = self.provider_combo.findData(config.get("ai_provider", "free_cloud"))
        if cur_prov_idx >= 0:
            self.provider_combo.setCurrentIndex(cur_prov_idx)

        self.api_key_input = QLineEdit(config.get("api_key", ""))
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Необязательно для Aski Free Cloud")

        self.base_url_input = QLineEdit(config.get("api_base_url", "https://api.openai.com/v1"))
        self.model_input = QLineEdit(config.get("model_name", "openai"))

        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.1, 1.5)
        self.temp_spin.setSingleStep(0.1)
        self.temp_spin.setValue(float(config.get("temperature", 0.8)))

        self.hist_spin = QSpinBox()
        self.hist_spin.setRange(4, 60)
        self.hist_spin.setValue(int(config.get("max_history_messages", 20)))

        form.addRow("Ваш никнейм:", self.nick_input)
        form.addRow("Тема оформления:", self.theme_combo)
        form.addRow("Провайдер ИИ:", self.provider_combo)
        form.addRow("API Ключ:", self.api_key_input)
        form.addRow("API Base URL:", self.base_url_input)
        form.addRow("Модель:", self.model_input)
        form.addRow("Креативность (Temp):", self.temp_spin)
        form.addRow("Глубина памяти (сообщ.):", self.hist_spin)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self._on_save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _on_save(self):
        config.set("user_nickname", self.nick_input.text().strip() or "User")
        config.set("theme", self.theme_combo.currentData())
        config.set("ai_provider", self.provider_combo.currentData())
        config.set("api_key", self.api_key_input.text().strip())
        config.set("api_base_url", self.base_url_input.text().strip())
        config.set("model_name", self.model_input.text().strip() or "openai")
        config.set("temperature", round(self.temp_spin.value(), 2))
        config.set("max_history_messages", int(self.hist_spin.value()))

        self.settingsChanged.emit()
        self.accept()
