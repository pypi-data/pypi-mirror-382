import asyncio
import logging
from abc import ABC

from pymodbus.client import AsyncModbusSerialClient

from ...models.device import ModbusConnection
from ...models.modbus_types import FramerType
from ...utils.modbus_utils import BaseModbusHandler


class SerialModbusClient(BaseModbusHandler, ABC):
    def __init__(self, connection: ModbusConnection):
        super().__init__()
        self.connection = connection
        if not connection.stop_bits:
            connection.stop_bits = 1
        if not connection.bytesize:
            connection.bytesize = 8
        if not connection.timeout:
            connection.timeout = 3
        if connection.retries < 0:
            connection.retries = 0
        if not connection.retries:
            connection.retries = 3
        if not connection.framer:
            connection.framer = FramerType.RTU
        
        # Create the client without initializing the event loop
        # This avoids the "no running event loop" error during initialization
        self.client = AsyncModbusSerialClient(
            port=connection.port,
            baudrate=connection.baud_rate,
            parity=connection.parity,
            stopbits=connection.stop_bits,
            bytesize=connection.bytesize,
            timeout=connection.timeout,
            retries=connection.retries,
            framer=connection.framer
        )
        
        # Patch the client's transaction manager to avoid event loop issues
        if hasattr(self.client, 'ctx') and hasattr(self.client.ctx, 'loop'):
            try:
                # Try to get the current event loop, or create a new one if none exists
                loop = asyncio.get_event_loop()
                self.client.ctx.loop = loop
            except RuntimeError:
                # If we're not in an event loop context, just set it to None for now
                # It will be properly set when connect() is called
                self.client.ctx.loop = None

    async def connect(self) -> None:
        if not self.client:
            logging.error(f"Error connecting to Modbus RTU device: empty client")
            return
        try:
            # If the loop wasn't set during initialization, set it now
            if hasattr(self.client, 'ctx') and hasattr(self.client.ctx, 'loop') and self.client.ctx.loop is None:
                self.client.ctx.loop = asyncio.get_running_loop()
                
            await self.client.connect()
            if not self.client.connected:
                raise ConnectionError(
                    f"Failed to connect to Modbus RTU device at {self.connection.port}"
                )
        except Exception as e:
            logging.error(f"Error connecting to Modbus RTU device: {str(e)}")
            return

    async def disconnect(self) -> None:
        if self.client:
            # Make sure to await the close method if it's a coroutine
            if asyncio.iscoroutinefunction(self.client.close):
                await self.client.close()
            else:
                self.client.close()
