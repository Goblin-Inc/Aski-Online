import json
from typing import Any, Dict
from .constants import CONFIG_PATH, DATA_DIR


DEFAULT_SETTINGS: Dict[str, Any] = {
    "user_nickname": "Denegen",
    "theme": "classic",
    "ai_provider": "free_cloud",
    "api_key": "",
    "api_base_url": "https://api.openai.com/v1",
    "model_name": "openai",
    "temperature": 0.8,
    "max_history_messages": 20,
    "show_contacts_panel": True,
    "active_contact_id": 1,
}


class AppConfig:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.path = CONFIG_PATH
        self.data: Dict[str, Any] = {}
        self.load()

    def load(self) -> Dict[str, Any]:
        merged = dict(DEFAULT_SETTINGS)
        if self.path.exists() and self.path.stat().st_size > 0:
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    merged.update(loaded)
            except Exception as e:
                print(f"[AskiOnline] Config load warning: {e}")
        self.data = merged
        self.save()
        return self.data

    def save(self) -> None:
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[AskiOnline] Config save warning: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
        self.save()


config = AppConfig()
