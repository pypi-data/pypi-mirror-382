from dataclasses import dataclass
from typing import Dict, Any

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Measurement:
    device_id: str
    device_type: str
    timestamp: int
    values: Dict[str, Any]

@dataclass_json
@dataclass
class ModBusMeasurement:
    client_id: str
    client_type: str
    data: Dict[str, Any]

    def __init__(self, measurement: Measurement):
        self.client_id = measurement.device_id
        if measurement.device_type == "electrical":
            self.client_type = "electrical_generation"
        elif measurement.device_type == "water":
            self.client_type = "water_generation"
        else:
            self.client_type: measurement.device_type
        self.data = {
            "client_id": measurement.device_id,
            "timestamp": measurement.timestamp,
            "delete_status": False,
        }
        for key, value in measurement.values.items():
            self.data[key] = value