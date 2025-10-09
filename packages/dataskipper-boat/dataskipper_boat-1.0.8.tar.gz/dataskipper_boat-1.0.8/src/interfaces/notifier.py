from abc import ABC, abstractmethod

from src.models.alert import Alert


class INotifier(ABC):
    @abstractmethod
    async def send_alert(self, alert: Alert) -> bool:
        """
        Send an alert through the notification channel.
        Returns True if successful, False otherwise.
        """
        pass