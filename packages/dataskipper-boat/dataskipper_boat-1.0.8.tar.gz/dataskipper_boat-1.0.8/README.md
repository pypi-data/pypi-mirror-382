# DataSkipper Boat

DataSkipper Boat is a Modbus monitoring application that reads data from Modbus devices, processes it, and sends measurements and alerts to various destinations.

## Features

- Supports both Modbus TCP and Modbus RTU (Serial)
- Reads registers from multiple Modbus devices
- Processes measurements and checks for threshold violations
- Generates alerts for threshold violations and significant changes
- Stores measurements and alerts locally
- Sends measurements and alerts to API endpoints
- Sends alerts to Discord (and optionally other notification channels)
- Handles connection failures and retries

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/dataskipper-boat.git
cd dataskipper-boat
```

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

The application uses YAML configuration files located in the `config` directory:

- `slave_config.yaml`: Configuration for Modbus connections and devices
- `communication.yaml`: Configuration for API endpoints, MQTT, and notification channels

### Environment Variables

- `CONFIG_DIR`: Path to the configuration directory (default: `~/config`)
- `DATA_DIR`: Path to the data directory (default: `~/data`)

### Logging Configuration

The application separates logs by severity level when running under supervisor:

- **stdout**: INFO level logs only
- **stderr**: WARNING, ERROR, and CRITICAL logs only
- **DEBUG logs**: Disabled by default

#### Changing Log Levels

To modify the logging behavior, edit `dataskipper_boat/main.py`:

1. **Enable DEBUG logs**:
   ```python
   root_logger.setLevel(logging.DEBUG)  # Change from logging.INFO
   stdout_handler.setLevel(logging.DEBUG)  # Accept DEBUG and above
   ```

2. **Change stdout filter** (currently only INFO):
   ```python
   # Modify or remove this line to change what goes to stdout
   stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)
   ```

3. **Change stderr minimum level** (currently WARNING):
   ```python
   stderr_handler.setLevel(logging.ERROR)  # Only ERROR and CRITICAL
   ```

4. **Send all logs to stdout** (no separation):
   ```python
   # Remove the stdout filter and stderr handler
   stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)  # Remove this line
   root_logger.removeHandler(stderr_handler)  # Remove stderr handler
   ```

After making changes, rebuild the package and restart supervisor services:
```bash
sudo supervisorctl restart ess1-lt ess1-ht ess1-relay
```

## Usage

To run the application:

```bash
python main.py
```

To reset water counters:

```bash
python reset_water_counter.py
```

## Testing

The application includes unit tests and integration tests. See [tests/README.md](tests/README.md) for more information on running the tests.

### Modbus Server Simulator

A Modbus server simulator is included for testing and development. To run the simulator:

```bash
python run_modbus_simulator.py
```

By default, the simulator will start on `localhost:5020`. You can specify a different host and port using the `--host` and `--port` options:

```bash
python run_modbus_simulator.py --host 0.0.0.0 --port 502
```

## Project Structure

- `main.py`: Main application entry point
- `reset_water_counter.py`: Script to reset water counters
- `src/`: Source code
  - `interfaces/`: Interface definitions
  - `models/`: Data models
  - `services/`: Services for communication with external systems
  - `utils/`: Utility functions
- `config/`: Configuration files
- `tests/`: Unit and integration tests

## Development

### Adding a New Device

To add a new Modbus device:

1. Add a new client configuration to `config/slave_config.yaml`
2. Define the registers to read from the device
3. Configure thresholds and alerts as needed

### Adding a New Notification Channel

To add a new notification channel:

1. Create a new notifier class in `src/services/notifiers/`
2. Implement the `INotifier` interface
3. Add the new notifier to the list of notifiers in `main.py`

## Releasing a New Version

To release a new version of DataSkipper Boat:

1. **Update version in pyproject.toml**:
   ```bash
   # Edit pyproject.toml and increment the version number
   version = "1.0.1"  # or whatever the new version is
   ```

2. **Build and upload to PyPI**:
   ```bash
   # Build the package
   python -m build
   
   # Upload to PyPI (requires PyPI account and API token)
   python -m twine upload dist/*
   ```

3. **Update target machines**:
   ```bash
   # On each target machine, run:
   sudo -u dcu pip3 install --user --upgrade dataskipper-boat
   sudo supervisorctl restart dataskipper-boat-*:*
   ```

## Setting Up a New Machine

To set up DataSkipper Boat on a new machine:

### Prerequisites
- Python 3.8+ installed
- Supervisor installed (`sudo apt install supervisor`)
- PyPI access (internet connection)

### Setup Steps

1. **Install the application**:
   ```bash
   # Install as user dcu (not root) to get correct paths
   sudo -u dcu pip3 install --user dataskipper-boat
   ```

2. **Create user and directories**:
   ```bash
   # Create user if it doesn't exist
   sudo useradd -m -s /bin/bash dcu
   
   # Create directories for each instance
   sudo mkdir -p /home/dcu/config_lt_panel /home/dcu/data_lt_panel
   sudo mkdir -p /home/dcu/config_ht_panel /home/dcu/data_ht_panel
   sudo mkdir -p /home/dcu/config_relay_panel /home/dcu/data_relay_panel
   sudo chown -R dcu:dcu /home/dcu/
   ```

3. **Install supervisor config**:
   ```bash
   # Copy supervisor config to target machine
   scp dataskipper-boat.conf target-machine:/tmp/
   
   # On target machine, install supervisor config
   sudo cp /tmp/dataskipper-boat.conf /etc/supervisor/conf.d/
   
   # Reload supervisor
   sudo supervisorctl reread
   sudo supervisorctl update
   ```

4. **Copy your configuration files**:
   ```bash
   # Copy your YAML config files to each instance directory:
   cp your_configs/slave_config.yaml /home/dcu/config_lt_panel/
   cp your_configs/communication.yaml /home/dcu/config_lt_panel/
   
   cp your_configs/slave_config.yaml /home/dcu/config_ht_panel/
   cp your_configs/communication.yaml /home/dcu/config_ht_panel/
   
   cp your_configs/slave_config.yaml /home/dcu/config_relay_panel/
   cp your_configs/communication.yaml /home/dcu/config_relay_panel/
   ```

5. **Start the processes**:
   ```bash
   sudo supervisorctl start dataskipper-boat-lt:*
   sudo supervisorctl start dataskipper-boat-ht:*
   sudo supervisorctl start dataskipper-boat-relay:*
   ```

6. **Verify everything is working**:
   ```bash
   # Check status
   sudo supervisorctl status
   
   # Check logs
   sudo supervisorctl tail -f dataskipper-boat-lt stderr
   ```

### Useful Management Commands
- **View status**: `sudo supervisorctl status`
- **Check logs**: `sudo supervisorctl tail -f dataskipper-boat-lt stderr`
- **Restart instance**: `sudo supervisorctl restart dataskipper-boat-lt:*`
- **Update application**: `sudo -u dcu pip3 install --user --upgrade dataskipper-boat && sudo supervisorctl restart dataskipper-boat-*:*`

## License

This project is proprietary software owned by DataSailors. All rights reserved. Unauthorized copying, modification, distribution, or use of this software is strictly prohibited. 