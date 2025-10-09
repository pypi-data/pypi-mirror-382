"""Utility classes for Modbus communication"""
import logging
from abc import ABC
from typing import Dict, Any, List
import asyncio

from pymodbus.client import ModbusTcpClient, ModbusSerialClient, AsyncModbusTcpClient, AsyncModbusSerialClient
from pymodbus.client.mixin import ModbusClientMixin

from src.interfaces.modbus_client import IModbusClient
from src.models.device import ModbusClient
from src.models.modbus_types import DataType, DATA_TYPE_MAPPING, RegisterType
from src.models.modbus_types import Endianness
from src.models.mqtt_trigger import WriteOperation


class BaseModbusHandler(IModbusClient, ABC):
    """Base implementation of ModbusConnectionHandler with common functionality"""

    def __init__(self):
        super().__init__()

    async def read_registers(self, client: ModbusClient) -> Dict[str, Any]:
        async with self.lock:
            result = {}
            if not client.registers:
                return result
            
            # Validate and ensure connection
            await self._ensure_connection()
            for register in client.registers:
                if register.count == 0:
                    count = self._get_register_count(register.data_type)
                else:
                    count = register.count
                logging.info(f"reading data for client: {client.id}, register: {register.address}")
                try:
                    if RegisterType(register.register_type) == RegisterType.InputRegister:
                        response = await self.client.read_input_registers(
                            address=register.address,
                            count=count,
                            slave=client.unit_id
                        )
                    elif RegisterType(register.register_type) == RegisterType.HoldingRegister:
                        response = await self.client.read_holding_registers(
                            address=register.address,
                            count=count,
                            slave=client.unit_id
                        )
                    else:
                        logging.error(f"Invalid register type: {register.register_type}, for register: {register.address}, of client id: {client.id}")
                    logging.info(f"Successfully read data for client: {client.id}, register: {register.address}")

                    if not response:
                        # await self.disconnect()
                        logging.warning(f"Got no response while reading data for client: {client.id}, register: {register.address}, returning.")
                        # return result
                        continue
                    if not response.isError():
                        register_values = response.registers if client.endianness == Endianness.BIG else response.registers[
                                                                                                         ::-1]
                        value = self.client.convert_from_registers(register_values, data_type=self._get_pymodbus_datatype_mapping(
                            data_type=register.data_type))
                        result[register.field_name] = value * register.multiplication_factor if register.multiplication_factor else value
                    else:
                        logging.error(f"Modbus error reading address {register.address}: {response}")
                except Exception as e:
                    await self.disconnect()
                    logging.error(f"Modbus error reading address {register.address} for client {client.id}: {e}")
                    return result
                await asyncio.sleep(0.05)

            await self.disconnect()
        return result

    async def write_registers(self, client: ModbusClient, operations: List[WriteOperation]) -> Dict[int, bool]:
        async with self.lock:
            results = {}
            
            # Validate and ensure connection
            await self._ensure_connection()
            
            for i, operation in enumerate(operations):
                try:
                    if operation.register_type == RegisterType.Coil:
                        response = await self.client.write_coil(
                            address=operation.address,
                            value=bool(operation.value),
                            slave=client.unit_id
                        )
                    elif operation.register_type == RegisterType.HoldingRegister:
                        # Convert value based on data type
                        data_type = DataType[operation.data_type]
                        pymodbus_type = self._get_pymodbus_datatype_mapping(data_type)
                        
                        # Apply multiplication factor if specified
                        value = operation.value
                        if operation.multiplication_factor:
                            value = value / operation.multiplication_factor
                            
                        registers = self.client.convert_to_registers(
                            value,
                            data_type=pymodbus_type,
                            number_of_registers=operation.count
                        )
                        
                        if client.endianness == Endianness.LITTLE:
                            registers = registers[::-1]
                            
                        if len(registers) == 1:
                            response = await self.client.write_register(
                                address=operation.address,
                                value=registers[0],
                                slave=client.unit_id
                            )
                        else:
                            response = await self.client.write_registers(
                                address=operation.address,
                                values=registers,
                                slave=client.unit_id
                            )
                    else:
                        logging.error(f"Unsupported register type for writing: {operation.register_type}")
                        results[i] = False
                        continue

                    results[i] = not response.isError() if response else False
                    
                    if not results[i]:
                        logging.error(f"Error writing to address {operation.address}: {response}")
                except Exception as e:
                    logging.error(f"Exception writing to address {operation.address}: {e}")
                    results[i] = False

            await self.disconnect()
            return results

    async def send_modbus_command(self, client: ModbusClient, command: bytes) -> bool:
        async with self.lock:
            if self.client.connected:
                await self.disconnect()
            try:
                # Create a new connection based on the client type
                if isinstance(self.client, AsyncModbusTcpClient):
                    new_client = ModbusTcpClient(
                        host=self.client.comm_params.host,
                        port=self.client.comm_params.port,
                        timeout=self.client.comm_params.timeout_connect,
                        retries=self.client.ctx.retries,
                    )
                elif isinstance(self.client, AsyncModbusSerialClient):  # Serial connection
                    new_client = ModbusSerialClient(
                        port=self.client.comm_params.host,
                        baudrate=self.client.comm_params.baudrate,
                        bytesize=self.client.comm_params.bytesize,
                        parity=self.client.comm_params.parity,
                        stopbits=self.client.comm_params.stopbits,
                        timeout=self.client.comm_params.timeout_connect,
                        retries=self.client.ctx.retries,
                    )
                else:
                    logging.error("Unrecognised client type")
                    return False
                if not new_client.connect():
                    logging.error("Failed to connect to Modbus device")
                    return False

                try:
                    logging.info(f"Sending command: {command.hex()}")
                    new_client.send(command)
                    return True
                except Exception as e:
                    logging.error(f"Exception sending command {command.hex()}: {e}")
                    return False
                finally:
                    new_client.close()

            except Exception as e:
                logging.error(f"Exception sending command {command.hex()}: {e}")
                return False
            finally:
                await self.disconnect()

    def _get_register_count(self, data_type: DataType) -> int:
        """Get the number of registers to read based on data type"""
        register_counts = {
            DataType.INT16.name: 1,
            DataType.INT32.name: 2,
            DataType.INT64.name: 4,
            DataType.UINT16.name: 1,
            DataType.UINT32.name: 2,
            DataType.UINT64.name: 4,
            DataType.FLOAT32.name: 2,
            DataType.FLOAT64.name: 4,
            DataType.STRING.name: 2,
        }
        return register_counts.get(data_type.name, 0)

    def _get_pymodbus_datatype_mapping(self, data_type: DataType) -> DataType:
        return DATA_TYPE_MAPPING.get(data_type.name, ModbusClientMixin.DATATYPE.FLOAT32)
    
    async def _ensure_connection(self, max_retries: int = 3) -> None:
        """Ensure the client is connected with retry logic."""
        for attempt in range(max_retries):
            try:
                if not self.client.connected:
                    logging.info(f"Attempting to connect (attempt {attempt + 1}/{max_retries})")
                    await self.client.connect()
                    
                if self.client.connected:
                    return
                    
            except Exception as e:
                logging.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1.0 * (attempt + 1))  # Exponential backoff
                    
        raise ConnectionError(f"Failed to establish connection after {max_retries} attempts")
    
    async def _validate_connection(self) -> bool:
        """Validate if the current connection is healthy."""
        if not self.client or not self.client.connected:
            return False
            
        try:
            # Try a simple read to validate connection health
            # This is a lightweight way to check if the connection is still alive
            if hasattr(self.client, 'transport') and self.client.transport:
                return not self.client.transport.is_closing()
            return True
        except Exception:
            return False

def _compute_crc(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

def build_flash_on_command(slave_id: int, flash_width_ms: int, channel: int) -> bytes:
    """Constructs the exact byte sequence for the flash command."""
    # Command structure: [SlaveID, 0x05, 0x02, RelayAddr, DelayHigh, DelayLow]
    func_code = 0x05  # Write Single Coil
    command = 0x02  # 0x02 = Flash ON
    
    logging.debug(f"Building flash command with: slave_id={slave_id}, flash_width_ms={flash_width_ms}, channel={channel}")
    
    flash_width_ms = int(flash_width_ms * 10)
    logging.debug(f"Adjusted flash_width_ms (multiply by 10): {flash_width_ms}")

    # Log individual byte values before construction
    logging.debug(f"Byte values to be used:")
    logging.debug(f"  slave_id: {slave_id} (0x{slave_id:02x})")
    logging.debug(f"  func_code: {func_code} (0x{func_code:02x})")
    logging.debug(f"  command: {command} (0x{command:02x})")
    logging.debug(f"  channel: {channel} (0x{channel:02x})")
    logging.debug(f"  flash_width_high: {(flash_width_ms >> 8) & 0xFF} (0x{((flash_width_ms >> 8) & 0xFF):02x})")
    logging.debug(f"  flash_width_low: {flash_width_ms & 0xFF} (0x{(flash_width_ms & 0xFF):02x})")

    # Construct the message (excluding CRC)
    try:
        msg = bytes([
            slave_id,
            func_code,
            command,
            channel,
            (flash_width_ms >> 8) & 0xFF,  # High byte of delay
            flash_width_ms & 0xFF  # Low byte of delay
        ])
        logging.debug(f"Successfully constructed message bytes: {msg.hex()}")
    except ValueError as e:
        logging.error(f"Failed to construct message bytes: {str(e)}")
        raise

    # Compute CRC16
    crc = _compute_crc(msg)
    crc_bytes = bytes([crc & 0xFF, (crc >> 8) & 0xFF])
    logging.debug(f"CRC bytes: {crc_bytes.hex()}")

    # Full command
    full_command = msg + crc_bytes
    logging.debug(f"Final command bytes: {full_command.hex()}")
    return full_command
