import logging
from typing import Dict, Any

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

from ..models.alert import Alert
from ..models.measurement import Measurement
from ..utils.common import human_readable_time


class APIService:
    def __init__(
            self,
            endpoints: Dict[str, Dict[str, Dict[str, Any]]],
            max_retries: int,
            retry_interval: int
    ):
        self.endpoints = endpoints
        self.max_retries = max_retries
        self.retry_interval = retry_interval

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def send_measurement(self, measurement: Measurement) -> bool:
        """Sends a measurement to the API. Logs errors without raising exceptions."""
        endpoint = self.endpoints[measurement.device_type]["measurements"]
        payload = {
            "client_id": measurement.device_id,
            "timestamp": measurement.timestamp,
        }
        nan_sample = False
        for k, v in measurement.values.items():
            if measurement.device_type.lower() == "electrical":
                if isinstance(v, list):
                    logging.warning(f"invalid data for: {measurement.device_id} at time: {human_readable_time(measurement.timestamp)}")
                    return True
                if str(v).lower() == "nan":
                    nan_sample = True
            payload[k] = v
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        endpoint["url"],
                        json=[payload],
                        headers=endpoint["headers"]
                ) as response:
                    if response.status == 200:
                        return True
                    else:
                        logging.error(f"Failed to send measurement: {response.status} {response.reason}")
                        logging.warning(f"invalid data for: {measurement.device_id} at time: {human_readable_time(measurement.timestamp)}")
                        return nan_sample
        except Exception as e:
            logging.error(f"Error sending measurement: {e}")
            return False  # Ensure the exception does not propagate

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def send_alert(self, alert: Alert) -> bool:
        """Sends an alert to the API. Logs errors without raising exceptions."""
        endpoint = self.endpoints[alert.device_type]["alerts"]
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        endpoint["url"],
                        json=[alert.to_dict()],
                        headers=endpoint["headers"]
                ) as response:
                    if response.status == 200:
                        return True
                    else:
                        logging.error(f"Failed to send alert: {response.status} {response.reason}")
                        return False
        except Exception as e:
            logging.error(f"Error sending alert: {e}")
            return False  # Ensure the exception does not propagate