from typing import Dict, List
from app.config import config
from backend.database.models import Contact
from .memory import ConversationMemory


class PromptBuilder:
    """Формирует живой системный промпт и цепочку сообщений для ИИ-собеседника."""

    @staticmethod
    def build_messages(contact: Contact, user_message: str) -> List[Dict[str, str]]:
        user_nick = config.get("user_nickname", "Denegen")
        memory_notes = ConversationMemory.update_memory_from_user_message(contact, user_message)

        system_parts = [
            f"Имя твоего персонажа: {contact.name} (UIN: {contact.uin}).",
            f"Твой статус в мессенджере: {contact.status} ({contact.status_note}).",
            f"Никнейм твоего собеседника: {user_nick}.",
            "Правила общения:",
            "1. Вы переписываетесь в ретро-мессенджере Aski Online (в духе ICQ). Общайся максимально живо, естественно и по-человечески.",
            "2. Никогда не говори, что ты языковая модель ИИ, и не используй канцелярские списки, если тебя специально не попросили написать код или инструкцию.",
            "3. Поддерживай диалог, помни контекст предыдущих реплик и отвечай в характере своего персонажа.",
            f"Описание твоего характера и роли:\n{contact.persona}",
        ]

        if memory_notes:
            system_parts.append(f"Что ты уже знаешь и помнишь о собеседнике ({user_nick}):\n{memory_notes}")

        system_prompt = "\n\n".join(system_parts)

        max_hist = int(config.get("max_history_messages", 20))
        history = ConversationMemory.build_history_messages(contact.id, limit=max_hist)

        messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
        messages.extend(history)

        if not history or history[-1].get("content") != user_message:
            messages.append({"role": "user", "content": user_message})

        return messages
