from dataclasses import dataclass, field
from enum import Enum
from typing import List, Any, Optional, Union

from dataclasses_json import dataclass_json

from src.models.modbus_types import RegisterType


class ConditionOperator(str, Enum):
    EQUALS = "equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    BETWEEN = "between"
    NOT_EQUALS = "not_equals"


class LogicalOperator(str, Enum):
    AND = "and"
    OR = "or"
    NOT = "not"


@dataclass_json
@dataclass
class WriteOperation:
    client_id: str
    address: int
    register_type: RegisterType
    value: Any
    data_type: str
    execution_order: int = 0  # Lower number = higher priority
    count: int = 1
    multiplication_factor: float = None
    pulse_time: Optional[float] = None  # Time in milliseconds for pulse duration if value is 'pulse', minimum value 100
    initial_delay: Optional[float] = None  # Time in seconds to wait before executing the operation


@dataclass_json
@dataclass
class Condition:
    client_id: str
    register_field: str
    operator: ConditionOperator
    value: Any = None
    min_value: Any = None
    max_value: Any = None


@dataclass_json
@dataclass
class CompositeCondition:
    operator: LogicalOperator
    conditions: List[Union[Condition, 'CompositeCondition']]


@dataclass_json
@dataclass
class ActionSet:
    write_operations: List[WriteOperation]
    response_topic: Optional[str] = None
    response_message: Optional[str] = None


@dataclass_json
@dataclass
class MQTTTrigger:
    topic: str
    message_pattern: str
    initial_condition: Optional[CompositeCondition] = None
    on_true_actions: ActionSet = field(default_factory=ActionSet)
    on_false_actions: ActionSet = field(default_factory=ActionSet)
    monitoring_interval: Optional[int] = None  # in seconds
    monitoring_condition: Optional[CompositeCondition] = None 