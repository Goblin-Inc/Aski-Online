import random
import sqlite3
from datetime import datetime
from typing import List, Optional

from app.constants import DATA_DIR, DB_PATH, DEFAULT_CONTACTS
from .models import Contact, Message


class Database:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.db_path = DB_PATH
        self._init_schema()
        self._seed_default_contacts()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uin TEXT NOT NULL,
                    name TEXT NOT NULL,
                    avatar TEXT NOT NULL DEFAULT '❀',
                    status TEXT NOT NULL DEFAULT '● Online',
                    status_note TEXT NOT NULL DEFAULT '',
                    persona TEXT NOT NULL,
                    memory_summary TEXT NOT NULL DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER NOT NULL,
                    sender TEXT NOT NULL,
                    sender_name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(contact_id) REFERENCES contacts(id) ON DELETE CASCADE
                );
                """
            )

    def _seed_default_contacts(self) -> None:
        with self._connect() as conn:
            count = conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
            if count > 0:
                return

            now_str = datetime.now().strftime("%H:%M")
            for item in DEFAULT_CONTACTS:
                cur = conn.execute(
                    """
                    INSERT INTO contacts (uin, name, avatar, status, status_note, persona)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item["uin"],
                        item["name"],
                        item["avatar"],
                        item["status"],
                        item["status_note"],
                        item["persona"],
                    ),
                )
                cid = cur.lastrowid
                greeting = item.get("greeting", "")
                if greeting:
                    conn.execute(
                        """
                        INSERT INTO messages (contact_id, sender, sender_name, content, timestamp)
                        VALUES (?, 'ai', ?, ?, ?)
                        """,
                        (cid, item["name"], greeting, now_str),
                    )
            conn.commit()

    def get_contacts(self) -> List[Contact]:
        contacts: List[Contact] = []
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM contacts ORDER BY id ASC").fetchall()
            for r in rows:
                last_msg = conn.execute(
                    "SELECT content FROM messages WHERE contact_id = ? ORDER BY id DESC LIMIT 1",
                    (r["id"],),
                ).fetchone()
                preview = last_msg["content"] if last_msg else r["status_note"]
                contacts.append(
                    Contact(
                        id=r["id"],
                        uin=r["uin"],
                        name=r["name"],
                        avatar=r["avatar"],
                        status=r["status"],
                        status_note=r["status_note"],
                        persona=r["persona"],
                        memory_summary=r["memory_summary"],
                        last_message_preview=preview,
                    )
                )
        return contacts

    def get_contact(self, contact_id: int) -> Optional[Contact]:
        with self._connect() as conn:
            r = conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
            if not r:
                return None
            return Contact(
                id=r["id"],
                uin=r["uin"],
                name=r["name"],
                avatar=r["avatar"],
                status=r["status"],
                status_note=r["status_note"],
                persona=r["persona"],
                memory_summary=r["memory_summary"],
            )

    def create_contact(
        self,
        name: str,
        avatar: str,
        status: str,
        status_note: str,
        persona: str,
        greeting: str = "",
    ) -> Contact:
        uin = f"{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(100,999)}"
        now_str = datetime.now().strftime("%H:%M")
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO contacts (uin, name, avatar, status, status_note, persona)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (uin, name, avatar or "❀", status or "● Online", status_note, persona),
            )
            cid = cur.lastrowid
            if greeting:
                conn.execute(
                    """
                    INSERT INTO messages (contact_id, sender, sender_name, content, timestamp)
                    VALUES (?, 'ai', ?, ?, ?)
                    """,
                    (cid, name, greeting, now_str),
                )
            conn.commit()
        return self.get_contact(cid)

    def delete_contact(self, contact_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM messages WHERE contact_id = ?", (contact_id,))
            conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
            conn.commit()

    def update_contact_memory(self, contact_id: int, memory_summary: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE contacts SET memory_summary = ? WHERE id = ?",
                (memory_summary, contact_id),
            )
            conn.commit()

    def add_message(self, contact_id: int, sender: str, sender_name: str, content: str) -> Message:
        now_str = datetime.now().strftime("%H:%M")
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO messages (contact_id, sender, sender_name, content, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (contact_id, sender, sender_name, content, now_str),
            )
            mid = cur.lastrowid
            conn.commit()
        return Message(
            id=mid,
            contact_id=contact_id,
            sender=sender,
            sender_name=sender_name,
            content=content,
            timestamp=now_str,
        )

    def get_messages(self, contact_id: int, limit: int = 100) -> List[Message]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM (
                    SELECT * FROM messages WHERE contact_id = ? ORDER BY id DESC LIMIT ?
                ) ORDER BY id ASC
                """,
                (contact_id, limit),
            ).fetchall()
            return [
                Message(
                    id=r["id"],
                    contact_id=r["contact_id"],
                    sender=r["sender"],
                    sender_name=r["sender_name"],
                    content=r["content"],
                    timestamp=r["timestamp"],
                )
                for r in rows
            ]

    def clear_messages(self, contact_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM messages WHERE contact_id = ?", (contact_id,))
            conn.commit()


db = Database()
