# Aski Online (Аська Онлайн)

**Aski Online** is a nostalgic 2000s-era desktop AI messenger inspired by classic **ICQ 2003a**, **Windows 98/2000**, and **Windows XP Luna**, built with **Python**, **PySide6**, and **SQLite**. Every contact in your roster has a unique UIN, status note, long-term memory, and distinct personality powered by LLM backends.

---

## ✨ Features

- **3 Switchable Retro Themes (`ui/styles/`):**
  - `Classic 2000 (Dark Slate)` — dark 3D-bevel retro interface (`classic.qss`)
  - `ICQ 2003a (Retro Gray)` — authentic classic ICQ gray bevel look (`icq.qss`)
  - `Windows XP Luna (Blue)` — iconic Windows XP blue title bar & warm dialogs (`xp.qss`)
- **Live AI Personas & Custom Contact Creator:**
  - Comes pre-loaded with 4 characters (*Лиза*, *x0r // Кибер-Хакер*, *Сократ // Философ*, *Макс // Код-Ревьюер*), each with their own UIN, status message, and conversational style.
  - Create unlimited custom AI contacts (`+ Контакт`) with custom avatars, status notes, and system prompts.
- **Multi-Provider AI Engine (`backend/ai/`):**
  - Works **out-of-the-box without API keys** via `Aski Free Cloud`, and also supports **Google Gemini API** and **OpenAI / Ollama / DeepSeek** endpoints.
- **Persistent SQLite History & Conversation Memory (`backend/database/`):**
  - Automatically stores all chat logs per contact and extracts key facts about the user into long-term persona memory.

---

## 🚀 Getting Started

```bash
python3 main.py
```
