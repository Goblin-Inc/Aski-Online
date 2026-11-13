import html
from backend.database.models import Message


class MessageFormatter:
    """Форматирует сообщения чата в аутентичном стиле мессенджера с поддержкой абзацев и блоков кода."""

    @staticmethod
    def format_message_html(msg: Message) -> str:
        is_user = msg.sender == "user"
        header_color = "#2563eb" if is_user else "#dc2626"
        bg_color = "rgba(37, 99, 235, 0.08)" if is_user else "rgba(16, 185, 129, 0.08)"
        border_color = "rgba(37, 99, 235, 0.25)" if is_user else "rgba(16, 185, 129, 0.25)"

        escaped_name = html.escape(msg.sender_name)
        escaped_time = html.escape(msg.timestamp)
        escaped_body = html.escape(msg.content).replace("\n", "<br>")

        return (
            f'<div style="margin-bottom: 10px; padding: 8px 10px; '
            f'background-color: {bg_color}; border-left: 3px solid {border_color};">'
            f'<div style="margin-bottom: 3px;">'
            f'<b style="color: {header_color};">{escaped_name}</b> '
            f'<span style="color: #6b7280; font-size: 9pt;">[{escaped_time}]</span>'
            f"</div>"
            f'<div style="line-height: 1.38;">{escaped_body}</div>'
            f"</div>"
        )
