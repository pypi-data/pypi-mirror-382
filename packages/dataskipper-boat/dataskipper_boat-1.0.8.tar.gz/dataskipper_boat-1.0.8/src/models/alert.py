from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from dataclasses_json import dataclass_json, config


class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AlertStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"

class AlertType(str, Enum):
    THRESHOLD_UPPER = "Upper Threshold Crossed"
    THRESHOLD_LOWER = "Lower Threshold Crossed"
    DELTA = "Delta"

@dataclass_json
@dataclass
class Alert:
    id: UUID = field(metadata=config(encoder=str, decoder=UUID))
    device_id: str
    device_type: str
    field_name: str
    alert_type: AlertType
    severity: AlertSeverity
    alert_status: AlertStatus
    message: str
    value: float
    timestamp: int
    threshold_value: float  # The threshold that triggered this alert
    previous_value: Optional[float] = None  # For delta alerts
    resolution_time: Optional[int] = None
    resolution_value: Optional[float] = None
    parent_alert_id: Optional[UUID] = field(
        default=None,
        metadata=config(encoder=str, decoder=UUID)  # Handle optional UUID
    )

    class Meta:
        encode_fields = {'alert_type': lambda x: x.value}
    
    @classmethod
    def create_threshold_alert(cls, device_id: str, device_type: str, field_name: str,
                             alert_type: AlertType, severity: AlertSeverity, 
                             message: str, value: float, threshold_value: float,
                             timestamp: int) -> 'Alert':
        return cls(
            id=uuid4(),
            device_id=device_id,
            device_type=device_type,
            field_name=field_name,
            alert_type=alert_type,
            severity=severity,
            alert_status=AlertStatus.ACTIVE,
            message=message,
            value=value,
            timestamp=timestamp,
            threshold_value=threshold_value
        )

    @classmethod
    def create_resolution_alert(cls, parent_alert: 'Alert', 
                              resolution_value: float,
                              resolution_time: int) -> 'Alert':
        return cls(
            id=uuid4(),
            device_id=parent_alert.device_id,
            device_type=parent_alert.device_type,
            field_name=parent_alert.field_name,
            alert_type=parent_alert.alert_type,
            severity=parent_alert.severity,
            alert_status=AlertStatus.RESOLVED,
            message=f"Alert resolved: {parent_alert.message}",
            value=resolution_value,
            timestamp=resolution_time,
            threshold_value=parent_alert.threshold_value,
            parent_alert_id=parent_alert.id,
            resolution_time=resolution_time,
            resolution_value=resolution_value,
            previous_value=parent_alert.value,
        )