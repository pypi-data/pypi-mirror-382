from abc import ABC, abstractmethod

from ..models.alert import Alert
from ..models.measurement import Measurement


class IStorage(ABC):
    @abstractmethod
    async def save_measurement(self, measurement: Measurement) -> None:
        pass

    @abstractmethod
    async def save_alert(self, alert: Alert) -> None:
        pass

    @abstractmethod
    async def get_pending_measurements(self) -> dict[str, Measurement]:
        pass

    @abstractmethod
    async def get_pending_alerts(self) -> dict[str, Alert]:
        pass

    async def save_pending_measurement(self, measurement: Measurement) -> None:
        pass

    async def save_pending_alert(self, alert: Alert) -> None:
        pass

    async def remove_pending_data(self, file_path: str) -> None:
        pass
