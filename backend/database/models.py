from dataclasses import dataclass
from typing import Optional


@dataclass
class Contact:
    id: int
    uin: str
    name: str
    avatar: str
    status: str
    status_note: str
    persona: str
    memory_summary: str = ""
    last_message_preview: str = ""
    unread_count: int = 0


@dataclass
class Message:
    id: Optional[int]
    contact_id: int
    sender: str  # "user" or "ai"
    sender_name: str
    content: str
    timestamp: str
