import re
from typing import Dict, List
from backend.database.database import db
from backend.database.models import Contact, Message


class ConversationMemory:
    """Управляет краткосрочным контекстом диалога и выделением ключевых фактов о пользователе."""

    FACT_PATTERNS = [
        re.compile(r"(?:меня зовут|моё имя|я\s+—)\s+([А-Яа-яA-Za-z0-9_]+)", re.IGNORECASE),
        re.compile(r"(?:я люблю|мне нравится|увлекаюсь)\s+([^.!?\n]{3,60})", re.IGNORECASE),
        re.compile(r"(?:я пишу на|программирую на|учу)\s+([^.!?\n]{2,50})", re.IGNORECASE),
        re.compile(r"(?:делаю проект|работаю над)\s+([^.!?\n]{3,60})", re.IGNORECASE),
    ]

    @classmethod
    def update_memory_from_user_message(cls, contact: Contact, user_text: str) -> str:
        existing_notes = [
            line.strip()
            for line in (contact.memory_summary or "").splitlines()
            if line.strip()
        ]
        for pattern in cls.FACT_PATTERNS:
            match = pattern.search(user_text)
            if match:
                fact = match.group(0).strip()
                if fact not in existing_notes:
                    existing_notes.append(fact)

        if len(existing_notes) > 12:
            existing_notes = existing_notes[-12:]

        summary = "\n".join(existing_notes)
        if summary != (contact.memory_summary or ""):
            db.update_contact_memory(contact.id, summary)
            contact.memory_summary = summary
        return summary

    @staticmethod
    def build_history_messages(contact_id: int, limit: int = 20) -> List[Dict[str, str]]:
        messages: List[Message] = db.get_messages(contact_id, limit=limit)
        formatted: List[Dict[str, str]] = []
        for m in messages:
            role = "user" if m.sender == "user" else "assistant"
            formatted.append({"role": role, "content": m.content})
        return formatted
