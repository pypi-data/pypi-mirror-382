import asyncio
import logging
import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path
import random
from typing import List

import yaml

# Configure logging with separate handlers for stdout and stderr
# Create formatters and handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Handler for INFO and below (stdout)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(formatter)
stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)

# Handler for WARNING and above (stderr)
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.WARNING)
stderr_handler.setFormatter(formatter)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)  # Set minimum level to INFO (no DEBUG)
root_logger.handlers = []  # Clear any existing handlers
root_logger.addHandler(stdout_handler)
root_logger.addHandler(stderr_handler)

from dataskipper_boat import __version__
from src.interfaces.modbus_client import IModbusClient
from src.models.alert import Alert
from src.models.device import ModbusConnection, create_modbus_connection, ModbusClient
from src.models.measurement import Measurement, ModBusMeasurement
from src.models.modbus_types import ConnectionType
from src.services.api_service import APIService
from src.services.modbus.serial_client import SerialModbusClient
from src.services.modbus.tcp_client import TcpModbusClient
from src.services.mqtt_service import MQTTService
from src.services.mqtt_trigger_service import MQTTTriggerService
from src.services.notifiers.discord_notifier import DiscordNotifier
from src.services.storage.file_storage import FileStorage
from src.utils.alert_checker import check_thresholds
from src.utils.common import async_api_handler


class ModbusMonitor:
    def __init__(self, config_dir: str):
        # Load configurations
        with open(Path(config_dir) / "slave_config.yaml") as f:
            connections_config = yaml.safe_load(f)

        with open(Path(config_dir) / "communication.yaml") as f:
            comm_config = yaml.safe_load(f)

        data_dir = os.getenv('DATA_DIR', os.path.join(os.path.expanduser('~'), "data"))

        # Initialize services
        storage = os.getenv('DATA_DIR', data_dir)
        self.storage = FileStorage(storage)

        # Initialize API and MQTT services first
        if comm_config.get('communication'):
            self.api_service = APIService(
                comm_config.get('communication')["api_endpoints"],
                comm_config.get('communication')["retry_config"]["max_retries"],
                comm_config.get('communication')["retry_config"]["interval"]
            )
            if comm_config.get('communication').get("mqtt_config"):
                # Initialize MQTT service without clients first
                self.mqtt_service = MQTTService(
                    comm_config.get('communication')["mqtt_config"]["host"],
                    comm_config.get('communication')["mqtt_config"]["port"],
                    comm_config.get('communication')["mqtt_config"]["username"],
                    comm_config.get('communication')["mqtt_config"]["password"],
                    comm_config.get('communication')["mqtt_config"]["topics"]
                )

        # Initialize notifiers
        self.notifiers = [
            DiscordNotifier(comm_config["discord_webhook_url"]),
            # Add Telegram notifier with your bot token and chat ID
            # TelegramNotifier("YOUR_BOT_TOKEN", "YOUR_CHAT_ID")
        ]

        # Initialize Modbus clients
        self.connections: List[ModbusConnection] = []
        self.clients = {}

        for conn in connections_config.get("connections"):
            connection = create_modbus_connection(conn)
            self.connections.append(connection)

            if ConnectionType(connection.connection_type) == ConnectionType.TCP:
                client = TcpModbusClient(connection)
            elif ConnectionType(connection.connection_type) == ConnectionType.SERIAL:
                client = SerialModbusClient(connection)
            else:
                logging.WARN(f"Invalid connection_type: {connection.connection_type} for connection: {connection.label}")
                continue

            self.clients[connection.id] = client
            
        if len(self.clients) == 0:
            raise ConnectionError("No connections")
            
        # Update MQTT service with clients after they are initialized
        if hasattr(self, 'mqtt_service'):
            self.mqtt_service.trigger_service = MQTTTriggerService(
                modbus_clients={client.id: client for connection in self.connections for client in connection.clients},
                modbus_connections={connection.id: connection for connection in self.connections}
            )
            self.mqtt_service.client.on_message = self.mqtt_service.on_message
            self.mqtt_service.subscribe_to_trigger_topics()

    async def process_alerts(self, alerts: List[Alert]) -> None:
        """Process and send alerts through all configured channels."""
        for alert in alerts:
            # Store alert locally
            # await self.storage.save_alert(alert)

            # Send to API
            try:
                await async_api_handler(first_method=self.api_service.send_alert, first_method_data=alert, result_of_first_method=False, second_method=self.storage.save_pending_alert, second_method_data=alert)
            except Exception as e:
                logging.error(f"Failed to send alert to API: {e}")

            # Send to MQTT
            try:
                if self.mqtt_service.client.is_connected():
                    self.mqtt_service.publish_alert(alert)
            except Exception as e:
                logging.error(f"Failed to send alert to MQTT: {e}")

            # Send to notifiers
            for notifier in self.notifiers:
                try:
                    await notifier.send_alert(alert)
                except Exception as e:
                    logging.error(f"Failed to send alert through notifier: {e}")

    async def monitor_client(self, reconnect_delay: float, modbus_client: ModbusClient, client: IModbusClient) -> None:
        """Monitor a single Modbus client and its devices."""
        initial_delay = random.uniform(0, 5)
        await asyncio.sleep(initial_delay)
        logging.info(f"Starting client with ID: {modbus_client.id} with unit_id: {modbus_client.unit_id} after initial delay of {initial_delay}")
        while True:
            try:
                start = datetime.now()
                # Read all registers
                values = await client.read_registers(modbus_client)
                if values:
                    # Create measurement
                    measurement = Measurement(
                        device_id=modbus_client.id,
                        device_type=modbus_client.type,
                        timestamp=int(time.time()),
                        values=values
                    )

                    # Send to API
                    if modbus_client.mqtt_preferred and modbus_client.mqtt_preferred_topic != "":
                        try:
                            if self.mqtt_service:
                                topic = modbus_client.mqtt_preferred_topic
                                modbus_measurement = ModBusMeasurement(measurement)
                                self.mqtt_service.publish_measurement(modbus_measurement, topic)
                        except Exception as e:
                            logging.error(f"Failed to send measurement to MQTT: {e}")
                    else:
                        try:
                            await async_api_handler(first_method=self.api_service.send_measurement, first_method_data=measurement, result_of_first_method=False, second_method=self.storage.save_pending_measurement, second_method_data=measurement)
                        except Exception as e:
                            logging.error(f"Failed to send measurement to API: {e}")

                        # Send to MQTT
                        try:
                            if self.mqtt_service:
                                topic = self.mqtt_service.topics[measurement.device_type]["measurements"]
                                self.mqtt_service.publish_measurement(measurement, topic)
                        except Exception as e:
                            logging.error(f"Failed to send measurement to MQTT: {e}")

                        # Check for alerts
                        alerts = []
                        previous_values = modbus_client.previous_values

                        for register in modbus_client.registers:
                            current_value = values[register.field_name]
                            previous_value = previous_values.get(register.field_name)

                            register_alerts = check_thresholds(
                                modbus_client.id,
                                modbus_client.type,
                                register,
                                current_value,
                                previous_value
                            )
                            alerts.extend(register_alerts)
                            # Update previous values
                            modbus_client.previous_values[register.field_name] = current_value

                        # Process alerts if any
                        if alerts:
                            await self.process_alerts(alerts)

                # Wait for polling interval
                end_time = datetime.now()
                diff = end_time - start
                if modbus_client.polling_interval - diff.total_seconds() > 0:
                    await asyncio.sleep(modbus_client.polling_interval - diff.total_seconds())
                else:
                    logging.warning(f"time taken to read and send measurement: {diff.total_seconds()} seconds while polling rate is: {modbus_client.polling_interval}, decrease the polling rate")

            except Exception as e:
                print(f"Error monitoring client {modbus_client.id}: {e}")
                await asyncio.sleep(reconnect_delay)

            # finally:
            #     await client.disconnect()

    async def start(self) -> None:
        """Start monitoring all Modbus connections."""
        tasks = []
        try:
            for connection in self.connections:
                client = self.clients[connection.id]
                for modbus_client in connection.clients:
                    if modbus_client.polling_interval:
                        task = asyncio.create_task(
                            self.monitor_client(connection.reconnect_delay, modbus_client, client)
                        )
                        tasks.append(task)
            task = asyncio.create_task(
                self.process_pending_measurements()
            )
            tasks.append(task)
            task = asyncio.create_task(
                self.process_pending_alerts()
            )
            tasks.append(task)

            # Wait for all tasks
            await asyncio.gather(*tasks)

        except KeyboardInterrupt:
            print("Keyboard interrupt received! Canceling tasks...")
            for task in tasks:
                task.cancel()

            # Optionally wait for tasks to be canceled
            await asyncio.gather(*tasks, return_exceptions=True)

            print("All tasks canceled.")

        finally:
            print("Cleaning up resources...")
            # Cancel and wait for all tasks to complete gracefully
            for task in tasks:
                if not task.done():
                    task.cancel()

            # Await cancellation of tasks to allow any cleanup
            await asyncio.gather(*tasks, return_exceptions=True)

            # Stop the monitor and disconnect clients
            await self.stop()

    async def stop(self) -> None:
        """Stop all Modbus connections."""
        for connection in self.connections:
            client = self.clients[connection.id]
            await client.disconnect()

    async def process_pending_measurements(self) -> None:
        while True:
            measurements = {}
            try:
                measurements = await self.storage.get_pending_measurements()
            except Exception as e:
                logging.error(f"Failed to get pending measurements: {e}")

            for file_name, measurement in measurements.items():
                sent = await self.api_service.send_measurement(measurement)
                if sent:
                    await self.storage.remove_pending_data(file_name)
                await asyncio.sleep(3)  # Short sleep after each measurement

            await asyncio.sleep(60)  # Longer sleep after processing all measurements

    async def process_pending_alerts(self) -> None:
        while True:
            alerts = {}
            try:
                alerts = await self.storage.get_pending_alerts()
            except Exception as e:
                logging.error(f"Failed to get pending alerts: {e}")

            for file_name, alert in alerts.items():
                sent = await self.api_service.send_alert(alert)
                if sent:
                    await self.storage.remove_pending_data(file_name)
                await asyncio.sleep(5)  # Short sleep after each alert

            await asyncio.sleep(60)  # Longer sleep after processing all alerts

async def async_main():
    config_dir = os.getenv('CONFIG_DIR', os.path.join(os.path.expanduser('~'), "config"))
    monitor = ModbusMonitor(config_dir)
    try:
        # Get the current event loop
        loop = asyncio.get_running_loop()
        # Initialize MQTT message processing if MQTT service exists
        if hasattr(monitor, 'mqtt_service'):
            await monitor.mqtt_service.start_processing(loop)
        await monitor.start()
    except KeyboardInterrupt:
        await monitor.stop()
    finally:
        print("Cleaning up resources...")

def main():
    """Entry point for the console script."""
    parser = argparse.ArgumentParser(description='DataSkipper Boat - IEC61850/Modbus monitoring, control and data collection system')
    parser.add_argument('--version', '-v', action='version', version=f'dataskipper-boat {__version__}')
    
    args = parser.parse_args()
    
    asyncio.run(async_main())

if __name__ == "__main__":
    main()