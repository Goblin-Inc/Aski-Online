import json
import random
import urllib.request
from typing import Dict, List
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

from app.config import config
from backend.database.models import Contact
from .promt_builder import PromptBuilder


class AIProvider:
    """Универсальный клиент ИИ (Free Cloud, Google Gemini, OpenAI/Ollama + умный локальный fallback)."""

    @classmethod
    def generate_reply(cls, contact: Contact, user_message: str) -> str:
        messages = PromptBuilder.build_messages(contact, user_message)
        provider_type = config.get("ai_provider", "free_cloud")
        api_key = (config.get("api_key", "") or "").strip()
        temperature = float(config.get("temperature", 0.8))

        # 1. Google Gemini API (если выбран и указан ключ)
        if provider_type == "gemini" and api_key:
            try:
                return cls._call_gemini(messages, api_key, temperature)
            except Exception as e:
                print(f"[AIProvider] Gemini error: {e}")

        # 2. OpenAI / Ollama / DeepSeek API
        if provider_type == "openai" and (api_key or "localhost" in config.get("api_base_url", "") or "127.0.0.1" in config.get("api_base_url", "")):
            try:
                return cls._call_openai_compatible(messages, api_key, temperature)
            except Exception as e:
                print(f"[AIProvider] OpenAI compatible error: {e}")

        # 3. Встроенный бесплатный облачный ИИ (Pollinations OpenAI endpoint — работает без ключа)
        try:
            return cls._call_free_cloud(messages, temperature)
        except Exception as e:
            print(f"[AIProvider] Free cloud warning: {e}")

        # 4. Локальный характерный ответ (на случай отсутствия интернета)
        return cls._offline_persona_reply(contact, user_message)

    @staticmethod
    def _call_free_cloud(messages: List[Dict[str, str]], temperature: float) -> str:
        payload = {
            "model": "openai",
            "messages": messages,
            "temperature": temperature,
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "https://text.pollinations.ai/openai",
            data=data_bytes,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "AskiOnline/1.0",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            content = body["choices"][0]["message"]["content"].strip()
            if content:
                return content
        raise RuntimeError("Empty response from free cloud")

    @staticmethod
    def _call_openai_compatible(messages: List[Dict[str, str]], api_key: str, temperature: float) -> str:
        base_url = (config.get("api_base_url", "https://api.openai.com/v1") or "").rstrip("/")
        model = config.get("model_name", "gpt-4o-mini") or "gpt-4o-mini"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        req = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body["choices"][0]["message"]["content"].strip()

    @staticmethod
    def _call_gemini(messages: List[Dict[str, str]], api_key: str, temperature: float) -> str:
        model = config.get("model_name", "gemini-2.0-flash")
        if not model.startswith("gemini"):
            model = "gemini-2.0-flash"

        system_instruction = ""
        contents = []
        for m in messages:
            if m["role"] == "system":
                system_instruction = m["content"]
            else:
                role = "user" if m["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": m["content"]}]})

        payload = {
            "contents": contents,
            "generationConfig": {"temperature": temperature},
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body["candidates"][0]["content"]["parts"][0]["text"].strip()

    @staticmethod
    def _offline_persona_reply(contact: Contact, user_message: str) -> str:
        name_lower = contact.name.lower()
        if "лиза" in name_lower:
            replies = [
                f"Ой, у меня на секунду моргнул коннект в Аське :) Ты написал: «{user_message[:40]}» — расскажи подробнее! ^_^",
                "Хах, звучит интересно! А что ты вообще планируешь делать сегодня вечером? 😊",
                "Слушай, у меня тут играет любимый плейлист, и твоё сообщение прям подняло настроение! ;)",
            ]
        elif "x0r" in name_lower or "хакер" in name_lower:
            replies = [
                "Пакеты дошли, хоть внешний шлюз слегка лагает. Что по коду — собирается без ворнингов?",
                "Принял. Если нужно поднять локальный демон или просканить порты — свисти.",
            ]
        elif "сократ" in name_lower:
            replies = [
                "Интересная мысль, друг мой. Но скажи: что стоит за этим стремлением на самом деле?",
                "В каждом вопросе уже скрыта половина ответа. Попробуй взглянуть на это с другой стороны.",
            ]
        else:
            replies = [
                "Принял сообщение! Давай разберём эту задачу детальнее.",
                "Отличная мысль. Какие следующие шаги планируешь?",
            ]
        return random.choice(replies)


class AIReplySignals(QObject):
    finished = Signal(int, str)  # contact_id, reply_text
    error = Signal(int, str)


class AIReplyTask(QRunnable):
    def __init__(self, contact: Contact, user_message: str):
        super().__init__()
        self.contact = contact
        self.user_message = user_message
        self.signals = AIReplySignals()

    @Slot()
    def run(self):
        try:
            reply = AIProvider.generate_reply(self.contact, self.user_message)
            self.signals.finished.emit(self.contact.id, reply)
        except Exception as e:
            self.signals.error.emit(self.contact.id, str(e))


class AIWorkerPool:
    def __init__(self):
        self.pool = QThreadPool.globalInstance()

    def request_reply(self, contact: Contact, user_message: str, on_finished, on_error=None):
        task = AIReplyTask(contact, user_message)
        task.signals.finished.connect(on_finished)
        if on_error:
            task.signals.error.connect(on_error)
        self.pool.start(task)


ai_worker = AIWorkerPool()
