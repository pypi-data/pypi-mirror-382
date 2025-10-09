from abc import ABC, abstractmethod
from asyncio import Lock
from typing import Dict, Any, List

from src.models.device import ModbusClient
from src.models.mqtt_trigger import WriteOperation


class IModbusClient(ABC):
    def __init__(self):
        self.lock = Lock()
        self.client = None

    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass

    @abstractmethod
    async def read_registers(self, client: ModbusClient) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def write_registers(self, client: ModbusClient, operations: List[WriteOperation]) -> Dict[str, bool]:
        """Write values to registers/coils.
        
        Args:
            client: The ModbusClient configuration
            operations: List of write operations to perform
            
        Returns:
            Dict mapping operation index to success status
        """
        pass

    @abstractmethod
    async def send_modbus_command(self, client: ModbusClient, command: bytes) -> bool:
        """Write values to registers/coils.

        Args:
            client: The ModbusClient configuration
            command: List of write operations to perform

        Returns:
            Boolean indicating success status
        """
        pass