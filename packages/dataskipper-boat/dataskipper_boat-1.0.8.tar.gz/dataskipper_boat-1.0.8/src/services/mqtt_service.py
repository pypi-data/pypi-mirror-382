import asyncio
import json
import logging
from queue import Queue, Empty
from threading import Thread, Event
from typing import Dict, Optional
import pkg_resources

import paho.mqtt.client as mqtt

from .mqtt_trigger_service import MQTTTriggerService
from ..models.alert import Alert
from ..models.device import ModbusClient, ModbusConnection
from ..models.measurement import Measurement, ModBusMeasurement


class MQTTService:
    def __init__(
            self,
            host: str,
            port: int,
            username: str,
            password: str,
            topics: Dict[str, Dict[str, str]],
            modbus_clients: Optional[Dict[str, ModbusClient]] = None,
            modbus_connections: Optional[Dict[str, ModbusConnection]] = None
    ):
        self.client = mqtt.Client()
        
        # Load CA certificate from package resources
        cert_path = pkg_resources.resource_filename('dataskipper_boat', 'emqxsl-ca.crt')
        self.client.tls_set(ca_certs=cert_path)
        
        self.client.username_pw_set(username, password)
        self.topics = topics
        self.message_queue = Queue()
        self.stop_event = Event()
        self.loop = None  # Store reference to event loop
        
        # Set up trigger service if Modbus clients are provided
        self.trigger_service = None
        if modbus_clients and modbus_connections:
            self.trigger_service = MQTTTriggerService(
                modbus_clients=modbus_clients,
                modbus_connections=modbus_connections
            )
            
        # Set up MQTT callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self.on_message
        
        try:
            logging.info("Connecting to MQTT broker...")
            self.client.connect(host, port)
            self.client.loop_start()
                
        except Exception as e:
            logging.error('Failed to connect with MQTT server: {}'.format(e))

    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connection is established"""
        logging.info(f"Connected to MQTT broker with result code: {rc}")
        if rc == 0 and self.trigger_service:
            self.subscribe_to_trigger_topics()

    def on_message(self, client, userdata, message):
        """Synchronous callback that queues messages for processing"""
        if not self.trigger_service:
            return
            
        try:
            logging.debug(f"Received MQTT message on topic: {message.topic}")
            self.message_queue.put((message.topic, message.payload))
            logging.debug("Successfully queued message for processing")
        except Exception as e:
            logging.error(f"Error queueing MQTT message: {e}")

    async def start_processing(self, loop):
        """Start message processing - called from main async context"""
        self.loop = loop
        self.stop_event.clear()
        # Start message processing in a separate thread
        self.process_thread = Thread(target=self._process_messages)
        self.process_thread.daemon = True
        self.process_thread.start()
        logging.info("Message processing thread started")

    def _process_messages(self):
        """Process messages in a separate thread"""
        while not self.stop_event.is_set():
            try:
                # Get message with timeout to allow checking stop_event
                try:
                    topic, payload = self.message_queue.get(timeout=0.1)
                except Empty:
                    continue

                logging.debug(f"Processing message from topic: {topic}")
                
                # Create future for async processing
                future = asyncio.run_coroutine_threadsafe(
                    self.trigger_service.handle_mqtt_message(
                        topic=topic,
                        message=payload.decode()
                    ),
                    self.loop
                )

                try:
                    # Wait for result with timeout
                    result = future.result(timeout=10)
                    
                    if result:
                        logging.debug(f"Message processing result: {result}")
                        # Send response if configured
                        if (
                            result.get("success") 
                            and "write_results" in result 
                            and all(result["write_results"].values())
                        ):
                            actions = result.get("on_true_actions")
                        else:
                            actions = result.get("on_false_actions")
                            
                        if actions:
                            # Handle both dictionary and ActionSet object cases
                            if isinstance(actions, dict):
                                response_topic = actions.get("response_topic")
                                response_message = actions.get("response_message")
                            else:
                                response_topic = actions.response_topic
                                response_message = actions.response_message
                            
                            if response_topic and response_message:
                                response = {
                                    "success": result.get("success", False),
                                    "message": response_message,
                                    "details": {
                                        "condition_values": result.get("condition_values", {}),
                                        "write_results": result.get("write_results", {})
                                    }
                                }
                                self.client.publish(
                                    response_topic,
                                    json.dumps(response)
                                )
                                logging.debug(f"Published response to: {response_topic}")
                            
                except Exception as e:
                    logging.error(f"Error processing MQTT message: {e}", exc_info=True)
                finally:
                    self.message_queue.task_done()
                    
            except Exception as e:
                logging.error(f"Error in message processing thread: {e}", exc_info=True)
                # Brief sleep on error to prevent tight loop
                self.stop_event.wait(1.0)

    def subscribe_to_trigger_topics(self):
        """Subscribe to all topics configured in triggers."""
        if not self.trigger_service:
            return
            
        topics = set()
        for client in self.trigger_service.modbus_clients.values():
            if not client.mqtt_triggers:
                continue
            for trigger in client.mqtt_triggers:
                if isinstance(trigger, dict):
                    topics.add(trigger.get('topic'))
                else:
                    topics.add(trigger.topic)
        
        for topic in topics:
            if topic:  # Only subscribe if topic is not None
                try:
                    self.client.subscribe(topic)
                    logging.info(f"Subscribed to trigger topic: {topic}")
                except Exception as e:
                    logging.error(f"Failed to subscribe to topic {topic}: {e}")

    def publish_measurement(self, measurement: [Measurement | ModBusMeasurement], topic: str) -> bool:
        if not topic:
            topic = self.topics[measurement.device_type]["measurements"]
        try:
            self.client.publish(
                topic,
                json.dumps(measurement.to_dict())
            )
            return True
        except Exception as e:
            logging.error('failed to publish measurement to MQTT server: {}'.format(e))
            return False

    def publish_alert(self, alert: Alert) -> bool:
        topic = self.topics[alert.device_type]["alerts"]
        try:
            self.client.publish(
                topic,
                json.dumps(alert.to_dict())
            )
            return True
        except:
            return False

    def disconnect(self):
        """Disconnect from MQTT broker and cleanup."""
        self.stop_event.set()
        if hasattr(self, 'process_thread'):
            self.process_thread.join(timeout=5.0)
        
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()