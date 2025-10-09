import logging

from telegram.ext import Application

from src.interfaces.notifier import INotifier
from src.models.alert import Alert
from src.utils.common import human_readable_time


class TelegramNotifier(INotifier):
    def __init__(self, bot_token: str, chat_id: str):
        self.application = Application.builder().token(bot_token).build()
        self.chat_id = chat_id

    async def send_alert(self, alert: Alert) -> bool:
        emoji_map = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
            "info": "🔵"
        }
        
        status_emoji = "🔴" if alert.alert_status == "active" else "✅"
        severity_emoji = emoji_map.get(alert.severity, "⚪")
        
        message = (
            f"{status_emoji} *Alert {alert.id}*\n"
            f"{severity_emoji} *Severity*: {alert.severity}\n"
            f"📱 *Device*: {alert.device_id} ({alert.device_type})\n"
            f"📊 *Field*: {alert.field_name}\n"
            f"📈 *Value*: {alert.value} (Threshold: {alert.threshold_value})\n"
            f"💬 *Message*: {alert.message}\n"
            f"🕒 *Time*: {human_readable_time(alert.timestamp).isoformat()}"
        )

        if alert.resolution_time:
            message += f"\n✅ *Resolved at*: {human_readable_time(alert.resolution_time).isoformat()}"
        
        if alert.parent_alert_id:
            message += f"\n🔗 *Parent Alert*: {alert.parent_alert_id}"

        try:
            await self.application.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            return True
        except Exception as e:
            logging.error(f"Failed to send Telegram alert: {e}")
            return False