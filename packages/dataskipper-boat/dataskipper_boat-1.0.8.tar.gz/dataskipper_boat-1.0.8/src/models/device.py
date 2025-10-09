from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict

from dataclasses_json import dataclass_json

from src.models.alert import AlertSeverity, Alert
from src.models.modbus_types import Endianness, RegisterType, ConnectionType, FramerType, DataType
from src.models.mqtt_trigger import (
    MQTTTrigger, WriteOperation, CompositeCondition
)


def parse_enum(enum_class, value):
    """Safely parse a string into an Enum value."""
    try:
        return enum_class(value)
    except ValueError:
        raise ValueError(f"Invalid value '{value}' for enum {enum_class.__name__}")

@dataclass_json
@dataclass(frozen=True)
class Threshold:
    value: Any
    message: str
    severity: AlertSeverity = AlertSeverity.INFO
    send_resolution_alert: bool = False

def create_thresholds(thresholds: List[dict]) -> List[Threshold]:
    """Create a list of Threshold objects from dictionaries."""
    return [Threshold(**t) for t in thresholds]

class AlertHistoryMetadata:
    def __init__(self):
        self.Triggered: bool = False
        self.Alert: Optional[Alert] = None


@dataclass_json
@dataclass
class Delta:
    value: float
    message: str
    severity: AlertSeverity = AlertSeverity.MEDIUM

def create_delta(delta: dict) -> List[Delta]:
    """Create a Delta object from a dictionary."""
    return [Delta(**t) for t in delta]


@dataclass_json
@dataclass
class Register:
    address: int
    count: int
    data_type: DataType
    field_name: str
    label: str
    unit: str
    register_type: RegisterType = RegisterType.HoldingRegister
    multiplication_factor: float = None
    upper_threshold: Optional[List[Threshold]] = None
    lower_threshold: Optional[List[Threshold]] = None
    delta: Optional[List[Delta]] = None
    AlertHistory: Optional[Dict[Threshold, AlertHistoryMetadata]] = None

def create_register(register_data: dict) -> Register:
    """Create a Register object, safely handling enum conversions."""
    register_data['data_type'] = parse_enum(DataType, register_data['data_type'])
    register_data['register_type'] = parse_enum(RegisterType, register_data.get('register_type', RegisterType.HoldingRegister.value))

    if 'upper_threshold' in register_data:
        register_data['upper_threshold'] = create_thresholds(register_data['upper_threshold'])
    if 'lower_threshold' in register_data:
        register_data['lower_threshold'] = create_thresholds(register_data['lower_threshold'])
    if 'delta' in register_data:
        register_data['delta'] = create_delta(register_data['delta'])

    reg = Register(**register_data)
    reg.AlertHistory = {}
    return reg

@dataclass_json
@dataclass
class ModbusClient:
    id: str
    type: str
    registers: List[Register]
    previous_values: Dict[str, Any] # {field_name: value}
    mqtt_triggers: Optional[List[MQTTTrigger]] = None
    active_monitors: Dict[str, Any] = field(default_factory=dict)  # Store running monitors

    mqtt_preferred: bool = False
    mqtt_preferred_topic: str = None
    polling_interval: int = 60
    unit_id: int = 1
    endianness: Endianness = Endianness.BIG


def create_modbus_client(client_data: dict) -> ModbusClient:
    """Create a ModbusClient object, safely handling enum conversions."""
    client_data['endianness'] = parse_enum(Endianness, client_data.get('endianness', Endianness.BIG.value))
    registers_def = client_data.get('registers')
    if registers_def:
        client_data['registers'] = [create_register(reg) for reg in registers_def]
    else:
        client_data['registers'] = []

    # Initialize previous values
    client_data['previous_values'] = {}

    # Convert MQTT triggers from dict to objects if present
    if 'mqtt_triggers' in client_data:
        triggers = []
        for trigger_data in client_data['mqtt_triggers']:
            # Convert write operations
            if 'on_true_actions' in trigger_data:
                write_ops = []
                for op in trigger_data['on_true_actions'].get('write_operations', []):
                    write_ops.append(WriteOperation.from_dict(op))
                trigger_data['on_true_actions']['write_operations'] = write_ops

            if 'on_false_actions' in trigger_data:
                write_ops = []
                for op in trigger_data['on_false_actions'].get('write_operations', []):
                    write_ops.append(WriteOperation.from_dict(op))
                trigger_data['on_false_actions']['write_operations'] = write_ops

            # Convert conditions
            if 'initial_condition' in trigger_data:
                trigger_data['initial_condition'] = CompositeCondition.from_dict(trigger_data['initial_condition'])
            if 'monitoring_condition' in trigger_data:
                trigger_data['monitoring_condition'] = CompositeCondition.from_dict(trigger_data['monitoring_condition'])

            # Convert the full trigger
            triggers.append(MQTTTrigger.from_dict(trigger_data))
        client_data['mqtt_triggers'] = triggers

    return ModbusClient(**client_data)


@dataclass_json
@dataclass
class ModbusConnection:
    id: str
    label: str
    connection_type: ConnectionType
    framer: FramerType
    clients: List[ModbusClient]

    timeout: int = 3
    retries: int = 3
    reconnect_delay: float = 0.1
    # TCP specific fields
    host: Optional[str] = None
    port: Any = None
    # Serial specific fields
    baud_rate: Optional[int] = None
    parity: Optional[str] = None
    stop_bits: Optional[int] = None
    bytesize: Optional[int] = None


def create_modbus_connection(connection_data: dict) -> ModbusConnection:
    """Create a ModbusConnection object, safely handling enum conversions and nested structures."""
    # Safely parse enum values
    _validate_modbbus_connection_config(connection_data)
    connection_data['connection_type'] = parse_enum(ConnectionType, connection_data['connection_type'])
    connection_data['framer'] = parse_enum(FramerType, connection_data['framer'])

    # Parse the clients list into ModbusClient objects
    connection_data['clients'] = [
        create_modbus_client(client) for client in connection_data['clients']
    ]

    # Return a ModbusConnection object
    return ModbusConnection(**connection_data)

def _validate_modbbus_connection_config(config: dict) -> None:
    connection_type = config.get('connection_type')
    if not connection_type:
        raise ValueError(f"No connection type specified in config for label: {config.get('label')}")
    if ConnectionType(connection_type) != ConnectionType.TCP and ConnectionType(connection_type) != ConnectionType.SERIAL:
        raise ValueError(f"Invalid connection type specified in config for label: {config.get('label')}")
    if ConnectionType(connection_type) == ConnectionType.TCP:
        if not config.get('host') or not config.get('port'):
            raise ValueError(f"No host or port specified in config for label: {config.get('label')}")
    if ConnectionType(connection_type) == ConnectionType.SERIAL:
        if not config.get('baud_rate') or not config.get('port'):
            raise ValueError(f"No baud_rate or port specified in config for label: {config.get('label')}")