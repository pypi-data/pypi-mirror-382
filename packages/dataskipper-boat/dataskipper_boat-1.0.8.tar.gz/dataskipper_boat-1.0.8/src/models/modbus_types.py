"""Common types and enums for Modbus communication"""
from enum import Enum
from typing import Union, Dict

from pymodbus.client.mixin import ModbusClientMixin

# Type aliases for better code readability
ModbusValue = Union[float, int]
RegisterMap = Dict[int, 'Register']  # Forward reference

class ConnectionType(str, Enum):
    TCP = "tcp"
    SERIAL = "serial"

class FramerType(str, Enum):
    """Type of Modbus frame."""
    ASCII = "ascii"
    RTU = "rtu"
    SOCKET = "socket"
    TLS = "tls"

class Endianness(str, Enum):
    BIG = "big"
    LITTLE = "little"

class RegisterType(str, Enum):
    InputRegister = "input"
    HoldingRegister = "holding"
    Coil = "coil"
    DiscreteInput = "discrete_input"

class DataType(str, Enum):
    INT16 = "int16"
    INT32 = "int32"
    INT64 = "int64"
    UINT16 = "uint16"
    UINT32 = "uint32"
    UINT64 = "uint64"
    FLOAT32 = "float"
    FLOAT64 = "float64"
    STRING = "string"
    BOOL = "bool"

DATA_TYPE_MAPPING = {
    DataType.INT16.name: ModbusClientMixin.DATATYPE.INT16,
    DataType.INT32.name: ModbusClientMixin.DATATYPE.INT32,
    DataType.INT64.name: ModbusClientMixin.DATATYPE.INT64,

    DataType.UINT16.name: ModbusClientMixin.DATATYPE.UINT16,
    DataType.UINT32.name: ModbusClientMixin.DATATYPE.UINT32,
    DataType.UINT64.name: ModbusClientMixin.DATATYPE.UINT64,

    DataType.FLOAT32.name: ModbusClientMixin.DATATYPE.FLOAT32,
    DataType.FLOAT64.name: ModbusClientMixin.DATATYPE.FLOAT64,

    DataType.STRING.name: ModbusClientMixin.DATATYPE.STRING,

    DataType.BOOL.name: "BOOL",
}
