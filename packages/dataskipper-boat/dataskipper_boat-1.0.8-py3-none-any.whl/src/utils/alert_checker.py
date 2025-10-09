import time
from typing import Optional, List

from src.models.alert import Alert, AlertType
from src.models.device import Register, AlertHistoryMetadata


def check_thresholds(
        device_id: str,
        device_type: str,
        register: Register,
        value: float,
        previous_value: Optional[float] = None
) -> List[Alert]:
    alerts = []
    timestamp = int(time.time())

    # Check upper thresholds
    if register.upper_threshold:
        for threshold in register.upper_threshold:
            if not register.AlertHistory.get(threshold):
                register.AlertHistory[threshold] = AlertHistoryMetadata()

            history = register.AlertHistory[threshold]

            if history.Triggered and threshold.send_resolution_alert:
                # Check for resolution
                if value <= threshold.value:
                    # Create resolution alert ONLY if send_resolution_alert is True
                    resolution_alert = Alert.create_resolution_alert(
                        parent_alert=history.Alert,
                        resolution_value=value,
                        resolution_time=timestamp
                    )
                    alerts.append(resolution_alert)
                    # Clean up history
                    del register.AlertHistory[threshold]
            elif history.Triggered and not threshold.send_resolution_alert:
                # Check for resolution but don't send alert
                if value <= threshold.value:
                    # Just clean up history without sending resolution alert
                    del register.AlertHistory[threshold]
            else:
                # No alert currently triggered
                if value > threshold.value:
                    # Create new alert
                    alert = Alert.create_threshold_alert(
                        device_id=device_id,
                        device_type=device_type,
                        field_name=register.field_name,
                        alert_type=AlertType.THRESHOLD_UPPER,
                        severity=threshold.severity,
                        message=threshold.message,
                        value=value,
                        threshold_value=threshold.value,
                        timestamp=timestamp
                    )
                    alerts.append(alert)
                    history.Triggered = True
                    history.Alert = alert

    # Check lower thresholds
    if register.lower_threshold:
        for threshold in register.lower_threshold:
            if not register.AlertHistory.get(threshold):
                register.AlertHistory[threshold] = AlertHistoryMetadata()

            history = register.AlertHistory[threshold]

            if history.Triggered and threshold.send_resolution_alert:
                # Send alert resolve message only if send_resolution_alert is True
                if value >= threshold.value:
                    resolution_alert = Alert.create_resolution_alert(
                        parent_alert=history.Alert,
                        resolution_value=value,
                        resolution_time=timestamp
                    )
                    alerts.append(resolution_alert)
                    # Clean up history
                    del register.AlertHistory[threshold]
            elif history.Triggered and not threshold.send_resolution_alert:
                # Check for resolution but don't send alert
                if value >= threshold.value:
                    # Just clean up history without sending resolution alert
                    del register.AlertHistory[threshold]
            else:
                # No alert currently triggered
                if value < threshold.value:
                    # Create new alert
                    alert = Alert.create_threshold_alert(
                        device_id=device_id,
                        device_type=device_type,
                        field_name=register.field_name,
                        alert_type=AlertType.THRESHOLD_LOWER,
                        severity=threshold.severity,
                        message=threshold.message,
                        value=value,
                        threshold_value=threshold.value,
                        timestamp=timestamp
                    )
                    alerts.append(alert)
                    history.Triggered = True
                    history.Alert = alert

    # Check delta
    if register.delta and previous_value is not None:
        for delta in register.delta:
            d = abs(value - previous_value)
            if d >= delta.value:
                alerts.append(Alert.create_threshold_alert(
                    device_id=device_id,
                    device_type=device_type,
                    field_name=register.field_name,
                    alert_type=AlertType.DELTA,
                    severity=delta.severity,
                    message=delta.message,
                    value=d,
                    threshold_value=delta.value,
                    timestamp=timestamp
                ))
    return alerts