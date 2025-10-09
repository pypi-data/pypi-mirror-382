import asyncio
import logging
import re
from typing import Dict, Any, List, Optional, Union

from src.models.device import ModbusClient, ModbusConnection
from src.models.modbus_types import ConnectionType
from src.models.mqtt_trigger import (
    MQTTTrigger, Condition, CompositeCondition, WriteOperation,
    ConditionOperator, LogicalOperator
)
from src.services.modbus.serial_client import SerialModbusClient
from src.services.modbus.tcp_client import TcpModbusClient
from src.utils.modbus_utils import build_flash_on_command


class MQTTTriggerService:
    def __init__(
        self, 
        modbus_clients: Dict[str, ModbusClient],
        modbus_connections: Dict[str, ModbusConnection]
    ):
        self.modbus_clients = modbus_clients
        self.modbus_connections = modbus_connections
        self.modbus_handlers: Dict[str, Union[TcpModbusClient, SerialModbusClient]] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}

    async def handle_mqtt_message(self, topic: str, message: str) -> Optional[Dict[str, Any]]:
        """Handle an incoming MQTT message and execute any matching triggers."""
        results = []
        
        for client in self.modbus_clients.values():
            if not client.mqtt_triggers:
                continue
                
            for trigger in client.mqtt_triggers:
                # Handle both dictionary and object cases
                trigger_topic = trigger.get('topic') if isinstance(trigger, dict) else trigger.topic
                trigger_pattern = trigger.get('message_pattern') if isinstance(trigger, dict) else trigger.message_pattern
                
                if trigger_topic != topic:
                    continue
                    
                if not re.search(trigger_pattern, message):
                    continue
                    
                result = await self._process_trigger(client, trigger, message)
                if result:
                    results.append(result)
        
        return results[0] if results else None

    async def _process_trigger(
        self, 
        client: ModbusClient, 
        trigger: Union[dict, MQTTTrigger], 
        message: str
    ) -> Optional[Dict[str, Any]]:
        """Process a single trigger that matches the incoming message."""
        result = {
            "trigger_topic": trigger.get('topic') if isinstance(trigger, dict) else trigger.topic,
            "message": message,
            "condition_values": {},
            "write_results": {},
            "success": False
        }

        # Evaluate initial condition if present
        initial_condition = trigger.get('initial_condition') if isinstance(trigger, dict) else trigger.initial_condition
        if initial_condition:
            condition_met, values = await self._evaluate_composite_condition(initial_condition)
            result["condition_values"].update(values)
        else:
            condition_met = True

        # Execute appropriate actions based on condition result
        if condition_met:
            actions = trigger.get('on_true_actions') if isinstance(trigger, dict) else trigger.on_true_actions
            write_ops = actions.get('write_operations') if isinstance(actions, dict) else actions.write_operations
            
            write_results = await self._execute_write_operations(write_ops)
            result["write_results"] = write_results
            result["success"] = all(write_results.values())
            
            # Start monitoring if configured
            monitoring_interval = trigger.get('monitoring_interval') if isinstance(trigger, dict) else trigger.monitoring_interval
            monitoring_condition = trigger.get('monitoring_condition') if isinstance(trigger, dict) else trigger.monitoring_condition
            
            if monitoring_interval and monitoring_condition and result["success"]:
                await self._start_monitoring(client, trigger)
        else:
            actions = trigger.get('on_false_actions') if isinstance(trigger, dict) else trigger.on_false_actions
            write_ops = actions.get('write_operations') if isinstance(actions, dict) else actions.write_operations
            
            write_results = await self._execute_write_operations(write_ops)
            result["write_results"] = write_results
            result["success"] = all(write_results.values())

        return result

    async def _evaluate_condition(self, condition: Condition) -> tuple[bool, Dict[str, Any]]:
        """Evaluate a single condition by reading the specified register."""
        client = self.modbus_clients.get(condition.client_id)
        if not client:
            logging.error(f"Client {condition.client_id} not found")
            return False, {}

        # Find the register
        register = next(
            (r for r in client.registers if r.field_name == condition.register_field),
            None
        )
        if not register:
            logging.error(
                f"Register {condition.register_field} not found in client {condition.client_id}"
            )
            return False, {}

        # Get or create handler
        handler = await self.get_or_create_handler(client)
        if not handler:
            return False, {}

        # Read the value
        values = await handler.read_registers(client)
        if condition.register_field not in values:
            return False, {}

        value = values[condition.register_field]
        result = {f"{condition.client_id}.{condition.register_field}": value}

        # Evaluate the condition
        if condition.operator == ConditionOperator.EQUALS:
            return value == condition.value, result
        elif condition.operator == ConditionOperator.NOT_EQUALS:
            return value != condition.value, result
        elif condition.operator == ConditionOperator.GREATER_THAN:
            return value > condition.value, result
        elif condition.operator == ConditionOperator.LESS_THAN:
            return value < condition.value, result
        elif condition.operator == ConditionOperator.BETWEEN:
            return condition.min_value <= value <= condition.max_value, result
        else:
            logging.error(f"Unknown operator: {condition.operator}")
            return False, result

    async def _evaluate_composite_condition(
        self, 
        condition: CompositeCondition
    ) -> tuple[bool, Dict[str, Any]]:
        """Evaluate a composite condition using logical operators."""
        results = []
        values = {}

        for cond in condition.conditions:
            if isinstance(cond, CompositeCondition):
                result, sub_values = await self._evaluate_composite_condition(cond)
                results.append(result)
                values.update(sub_values)
            else:
                result, sub_values = await self._evaluate_condition(cond)
                results.append(result)
                values.update(sub_values)

        if condition.operator == LogicalOperator.AND:
            return all(results), values
        elif condition.operator == LogicalOperator.OR:
            return any(results), values
        elif condition.operator == LogicalOperator.NOT:
            return not any(results), values
        else:
            logging.error(f"Unknown logical operator: {condition.operator}")
            return False, values

    async def _execute_write_operations(
        self, 
        operations: List[WriteOperation]
    ) -> Dict[str, bool]:
        """Execute a list of write operations."""
        results = {}
        
        # Sort operations by execution_order
        sorted_operations = sorted(operations, key=lambda x: x.execution_order)
        
        for operation in sorted_operations:
            client = self.modbus_clients.get(operation.client_id)
            if not client:
                logging.error(f"Client {operation.client_id} not found")
                continue

            handler = await self.get_or_create_handler(client)
            if not handler:
                continue

            # Handle initial delay if specified
            if operation.initial_delay is not None and operation.initial_delay > 0:
                await asyncio.sleep(operation.initial_delay)

            # Handle pulse operation
            if isinstance(operation.value, str) and operation.value.lower() == 'pulse':
                if operation.pulse_time is None:
                    logging.warning(f"Pulse time not specified for pulse operation on {operation.client_id}")
                    operation.pulse_time = 5

                pulse_command = build_flash_on_command(client.unit_id, operation.pulse_time, operation.address)
                write_result = await handler.send_modbus_command(client, pulse_command)

                results[f"{operation.client_id}.{operation.address}"] = write_result
            else:
                # Normal write operation
                write_results = await handler.write_registers(client, [operation])
                results[f"{operation.client_id}.{operation.address}"] = write_results.get(0, False)

        return results


    async def _start_monitoring(self, client: ModbusClient, trigger: MQTTTrigger):
        """Start a monitoring task for a trigger."""
        # Cancel existing monitoring task if any
        if trigger.topic in self.monitoring_tasks:
            self.monitoring_tasks[trigger.topic].cancel()
            
        # Create new monitoring task
        task = asyncio.create_task(
            self._monitor_condition(client, trigger)
        )
        self.monitoring_tasks[trigger.topic] = task

    async def _monitor_condition(self, client: ModbusClient, trigger: MQTTTrigger):
        """Monitor a condition at regular intervals."""
        while True:
            try:
                condition_met, _ = await self._evaluate_composite_condition(
                    trigger.monitoring_condition
                )
                
                if not condition_met:
                    # Execute false actions when condition is no longer met
                    await self._execute_write_operations(
                        trigger.on_false_actions.write_operations
                    )
                    # Stop monitoring
                    break
                    
                await asyncio.sleep(trigger.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in monitoring task: {e}")
                break

        # Remove task from tracking
        self.monitoring_tasks.pop(trigger.topic, None)

    async def cleanup(self):
        """Clean up all handlers and monitoring tasks."""
        # Cancel all monitoring tasks
        for task in self.monitoring_tasks.values():
            if not task.done():
                task.cancel()
        self.monitoring_tasks.clear()
        
        # Disconnect all handlers
        for handler in self.modbus_handlers.values():
            try:
                await handler.disconnect()
            except Exception as e:
                logging.error(f"Error disconnecting handler: {e}")
        self.modbus_handlers.clear()

    async def get_or_create_handler(
        self, 
        client: ModbusClient
    ) -> Optional[Union[TcpModbusClient, SerialModbusClient]]:
        """Get or create a Modbus handler for a client with connection validation."""
        handler = self.modbus_handlers.get(client.id)
        
        # Check if existing handler is still connected
        if handler and hasattr(handler, 'client') and handler.client:
            if not handler.client.connected:
                logging.info(f"Handler for client {client.id} is disconnected, removing and recreating")
                try:
                    await handler.disconnect()
                except Exception as e:
                    logging.error(f"Error disconnecting stale handler: {e}")
                del self.modbus_handlers[client.id]
                handler = None
        
        if not handler:
            # Find the connection for this client
            connection = next(
                (
                    conn for conn in self.modbus_connections.values()
                    if any(c.id == client.id for c in conn.clients)
                ),
                None
            )
            
            if not connection:
                logging.error(f"No connection configuration found for client {client.id}")
                return None

            try:
                if connection.connection_type == ConnectionType.TCP:
                    handler = TcpModbusClient(connection)
                else:
                    handler = SerialModbusClient(connection)
                    
                await handler.connect()
                if handler.client and handler.client.connected:
                    self.modbus_handlers[client.id] = handler
                else:
                    logging.error(f"Failed to establish connection for client {client.id}")
                    return None
                
            except Exception as e:
                logging.error(f"Failed to create handler for client {client.id}: {e}")
                return None

        return handler