import logging

import aiohttp

from ...interfaces.notifier import INotifier
from ...models.alert import Alert
from ...utils.common import human_readable_time


class DiscordNotifier(INotifier):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send_alert(self, alert: Alert) -> bool:
        severity_colors = {
            "critical": 0xFF0000,  # Red
            "high": 0xFFA500,      # Orange
            "medium": 0xFFFF00,    # Yellow
            "low": 0x00FF00,       # Green
            "info": 0x0000FF       # Blue
        }

        embed = {
            "title": f"Alert {alert.id}",
            "color": severity_colors.get(alert.severity, 0x808080),
            "fields": [
                {"name": "Alert Status", "value": alert.alert_status, "inline": True},
                {"name": "Severity", "value": alert.severity, "inline": True},
                {"name": "Device", "value": f"{alert.device_id} ({alert.device_type})", "inline": True},
                {"name": "Field", "value": alert.field_name, "inline": True},
                {"name": "Value", "value": str(alert.value), "inline": True},
                {"name": "Threshold", "value": str(alert.threshold_value), "inline": True},
                {"name": "Message", "value": alert.message},
                {"name": "Time", "value": human_readable_time(alert.timestamp).isoformat()}
            ]
        }

        if alert.resolution_time:
            embed["fields"].append({
                "name": "Resolved at",
                "value": human_readable_time(alert.resolution_time).isoformat()
            })

        if alert.parent_alert_id:
            embed["fields"].append({
                "name": "Parent Alert",
                "value": str(alert.parent_alert_id)
            })

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json={"embeds": [embed]}
                ) as response:
                    return response.status == 204
        except Exception as e:
            logging.error(f"Failed to send Discord alert: {e}")
            return False
