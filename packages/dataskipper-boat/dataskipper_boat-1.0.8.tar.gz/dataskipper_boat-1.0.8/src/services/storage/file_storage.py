import enum
import json
import logging
import os
from datetime import datetime

from tenacity import retry, stop_after_attempt, wait_exponential

from src.interfaces.storage import IStorage
from src.models.alert import Alert
from src.models.measurement import Measurement
from src.utils.common import human_readable_time


class Status(str, enum.Enum):
    PENDING = 'pending'
    PROCESSED = 'processed'


class FileStorage(IStorage):
    def __init__(self, base_path: str):
        self.measurements_path = os.path.join(base_path, "measurements")
        self.alerts_path = os.path.join(base_path, "alerts")
        self.pending_path = os.path.join(base_path, "pending")
        self.pending_alert_path = os.path.join(base_path, "pending", "alerts")
        self.pending_measurement_path = os.path.join(base_path, "pending", "measurements")

        # Create all required directories
        for path in [base_path, self.measurements_path, self.alerts_path, 
                    self.pending_path, self.pending_alert_path, 
                    self.pending_measurement_path]:
            os.makedirs(path, exist_ok=True)

    async def save_measurement(self, measurement: Measurement) -> None:
        """Save measurement data to file system."""
        filename = f"{measurement.device_id}_{human_readable_time(measurement.timestamp)}.json"
        path = os.path.join(self.measurements_path, filename)
        if isinstance(measurement.timestamp, datetime):
            measurement.timestamp = measurement.timestamp.timestamp()

        with open(path, 'w') as f:
            json.dump(measurement.to_dict(), f)

    async def save_alert(self, alert: Alert) -> None:
        """Save alert with UUID as filename for easy lookup and tracking."""
        filename = f"{alert.id}.json"
        path = os.path.join(self.alerts_path, filename)
        
        # Convert UUIDs to strings for JSON serialization
        alert_dict = alert.to_dict()
        alert_dict['id'] = str(alert_dict['id'])
        if alert_dict.get('parent_alert_id'):
            alert_dict['parent_alert_id'] = str(alert_dict['parent_alert_id'])

        with open(path, 'w') as f:
            json.dump(alert_dict, f)

    async def save_pending_measurement(self, measurement: Measurement) -> None:
        """Save pending measurement with status tracking."""
        filename = f"{measurement.device_id}_{human_readable_time(measurement.timestamp)}.json"
        path = os.path.join(self.pending_measurement_path, filename)
        if isinstance(measurement.timestamp, datetime):
            measurement.timestamp = measurement.timestamp.timestamp()
        
        data = measurement.to_dict()
        data["processing_status"] = Status.PENDING.value

        with open(path, 'w') as f:
            json.dump(data, f)

    async def save_pending_alert(self, alert: Alert) -> None:
        """Save pending alert with UUID and status tracking."""
        filename = f"{alert.id}.json"
        path = os.path.join(self.pending_alert_path, filename)
        
        alert_dict = alert.to_dict()
        alert_dict['id'] = str(alert_dict['id'])
        if alert_dict.get('parent_alert_id'):
            alert_dict['parent_alert_id'] = str(alert_dict['parent_alert_id'])
        alert_dict["processing_status"] = Status.PENDING.value

        with open(path, 'w') as f:
            json.dump(alert_dict, f)

    async def get_pending_measurements(self) -> dict[str, Measurement]:
        """Retrieve all pending measurements."""
        pending = {}
        pending_dir = os.path.join(self.pending_measurement_path)

        if not os.path.exists(pending_dir):
            return pending

        process_file_count = 0
        for filename in os.listdir(pending_dir):
            if process_file_count > 10:
                break
            path = os.path.join(pending_dir, filename)
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    pending[path] = Measurement.from_dict(data)
                    process_file_count += 1
            except Exception as e:
                logging.error(f"Error reading pending measurement {filename}: {e}")
                continue

        return pending

    async def get_pending_alerts(self) -> dict[str, Alert]:
        """Retrieve all pending alerts with UUID handling."""
        pending = {}
        pending_dir = os.path.join(self.pending_alert_path)

        if not os.path.exists(pending_dir):
            return pending

        process_file_count = 0
        for filename in os.listdir(pending_dir):
            if process_file_count > 10:
                break
            path = os.path.join(pending_dir, filename)
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    data = preprocess_data(data=data)
                    pending[path] = Alert.from_dict(data)
                    process_file_count += 1
            except Exception as e:
                logging.error(f"Error reading pending alert {filename}: {e}")
                continue

        return pending

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def remove_pending_data(self, file_path: str) -> None:
        """Remove pending data file with retry mechanism."""
        try:
            os.remove(file_path)
            logging.info(f"Successfully removed pending file: {file_path}")
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
        except PermissionError:
            logging.error(f"Permission denied: Cannot delete {file_path}")
        except Exception as e:
            logging.error(f"Error removing pending file {file_path}: {e}")
            raise

def preprocess_data(data):
    # Traverse the dictionary and replace "None" with None
    for key, value in data.items():
        if value == "None":  # Replace string "None" with None
            data[key] = None
        elif isinstance(value, dict):  # Recurse into nested dictionaries
            preprocess_data(value)
        elif isinstance(value, list):  # Process lists of dictionaries
            for item in value:
                if isinstance(item, dict):
                    preprocess_data(item)
    return data
