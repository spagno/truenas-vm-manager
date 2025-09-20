# API Reference

## Overview

This document provides detailed API reference for the TrueNAS VM Manager classes and methods.

## Core Classes

### TemplateManager

The `TemplateManager` class handles loading and processing of JSON templates for VM and device configurations.

#### Constructor

```python
TemplateManager(base_path: Path = None)
```

**Parameters:**
- `base_path` (Path, optional): Base directory for template files. Defaults to script directory.

**Raises:**
- `TrueNASError`: If template files are not found or contain invalid JSON

#### Methods

##### create_vm_spec()

```python
create_vm_spec(name: str, cores: int, threads: int, memory: int) -> Dict[str, Any]
```

Creates a VM specification from the base VM template.

**Parameters:**
- `name` (str): VM name
- `cores` (int): Number of CPU cores
- `threads` (int): Number of CPU threads
- `memory` (int): RAM in MB

**Returns:**
- `Dict[str, Any]`: Complete VM specification ready for TrueNAS API

**Example:**
```python
template_manager = TemplateManager()
vm_spec = template_manager.create_vm_spec("test-vm", 4, 4, 8192)
```

##### create_display_device()

```python
create_display_device(vm_id: int, port: int, password: str) -> Dict[str, Any]
```

Creates a SPICE display device configuration.

**Parameters:**
- `vm_id` (int): VM identifier from TrueNAS
- `port` (int): SPICE display port
- `password` (str): SPICE access password

**Returns:**
- `Dict[str, Any]`: SPICE display device configuration

##### create_cdrom_device()

```python
create_cdrom_device(vm_id: int, path: str) -> Dict[str, Any]
```

Creates a CDROM device configuration.

**Parameters:**
- `vm_id` (int): VM identifier from TrueNAS
- `path` (str): Path to ISO file

**Returns:**
- `Dict[str, Any]`: CDROM device configuration

##### create_nic_device()

```python
create_nic_device(vm_id: int, nic_attach: str, mac: str = None) -> Dict[str, Any]
```

Creates a network interface device configuration.

**Parameters:**
- `vm_id` (int): VM identifier from TrueNAS
- `nic_attach` (str): Bridge interface name
- `mac` (str, optional): MAC address for the interface

**Returns:**
- `Dict[str, Any]`: Network interface device configuration

##### create_disk_device()

```python
create_disk_device(vm_id: int, zvol_name: str, size_bytes: int) -> Dict[str, Any]
```

Creates a disk device configuration.

**Parameters:**
- `vm_id` (int): VM identifier from TrueNAS
- `zvol_name` (str): ZVOL path (e.g., "pool/VMs/vm-name-disk0")
- `size_bytes` (int): Disk size in bytes

**Returns:**
- `Dict[str, Any]`: Disk device configuration

---

### VMManager

The `VMManager` class manages VM operations on TrueNAS systems.

#### Constructor

```python
VMManager(host: str, username: str, password: str, vnc_password: str, template_manager: TemplateManager = None)
```

**Parameters:**
- `host` (str): TrueNAS hostname or IP address
- `username` (str): TrueNAS API username
- `password` (str): TrueNAS API password
- `vnc_password` (str): Password for SPICE display access
- `template_manager` (TemplateManager, optional): Template manager instance

#### Context Manager

The `VMManager` class supports context manager protocol for automatic connection management:

```python
with VMManager(host, user, pwd, vnc_pwd) as vm_manager:
    vm_manager.create_vm_type(config, "controlplane", 5910)
```

#### Methods

##### connect()

```python
connect() -> None
```

Establishes connection to TrueNAS API.

**Raises:**
- `TrueNASError`: If connection or authentication fails

##### disconnect()

```python
disconnect() -> None
```

Closes connection to TrueNAS API.

##### create_vm_type()

```python
create_vm_type(config: Dict[str, Any], vm_type: str, vnc_start_port: int) -> None
```

Creates multiple VMs of a specific type.

**Parameters:**
- `config` (Dict[str, Any]): Configuration dictionary from YAML
- `vm_type` (str): VM type ("controlplane" or "worker")
- `vnc_start_port` (int): Starting port for SPICE displays

**Raises:**
- `TrueNASError`: If VM type not found or storage configuration missing

**Example:**
```python
with VMManager(host, user, pwd, vnc_pwd) as vm_manager:
    vm_manager.create_vm_type(config, "controlplane", 5910)
    vm_manager.create_vm_type(config, "worker", 5920)
```

##### destroy_managed_vms()

```python
destroy_managed_vms(vm_prefixes: List[str] = None) -> None
```

Destroys VMs with specified name prefixes.

**Parameters:**
- `vm_prefixes` (List[str], optional): VM name prefixes to match. Defaults to ["controlplane", "worker"]

**Example:**
```python
# Destroy all managed VMs
vm_manager.destroy_managed_vms()

# Destroy only controlplane VMs
vm_manager.destroy_managed_vms(["controlplane"])
```

##### Private Methods

###### _create_single_vm()

```python
_create_single_vm(vm_name: str, vm_config: Dict[str, Any], vnc_port: int, storage_config: Dict[str, Any]) -> None
```

Creates a single VM with all its devices.

**Parameters:**
- `vm_name` (str): Name for the VM
- `vm_config` (Dict[str, Any]): VM type configuration
- `vnc_port` (int): SPICE display port
- `storage_config` (Dict[str, Any]): Storage configuration

###### _create_vm_devices()

```python
_create_vm_devices(vm_id: int, vm_name: str, vm_config: Dict[str, Any], vnc_port: int, storage_config: Dict[str, Any]) -> None
```

Creates and attaches devices to a VM.

**Parameters:**
- `vm_id` (int): VM identifier from TrueNAS
- `vm_name` (str): VM name for ZVOL naming
- `vm_config` (Dict[str, Any]): VM type configuration
- `vnc_port` (int): SPICE display port
- `storage_config` (Dict[str, Any]): Storage configuration

###### _add_device()

```python
_add_device(device: Dict[str, Any]) -> None
```

Adds a device to a VM via TrueNAS API.

**Parameters:**
- `device` (Dict[str, Any]): Device configuration

**Raises:**
- `TrueNASError`: If device creation fails

---

## Configuration Functions

### load_configuration()

```python
load_configuration(config_path: str = "config.yaml") -> Dict[str, Any]
```

Loads and validates configuration from YAML file.

**Parameters:**
- `config_path` (str): Path to configuration file

**Returns:**
- `Dict[str, Any]`: Validated configuration dictionary

**Raises:**
- `FileNotFoundError`: If configuration file doesn't exist
- `ValueError`: If configuration is invalid or missing required sections
- `yaml.YAMLError`: If YAML syntax is invalid

**Required Configuration Sections:**
- `storage`: Storage configuration with `pool_path` and `cdrom_path`
- `controlplane`: Controlplane VM configuration
- `worker`: Worker VM configuration

### get_environment_variables()

```python
get_environment_variables() -> tuple[str, str, str, str]
```

Loads and validates environment variables.

**Returns:**
- `tuple[str, str, str, str]`: (truenas_host, api_username, api_password, vnc_password)

**Raises:**
- `ValueError`: If required environment variables are missing

**Required Environment Variables:**
- `TRUENAS_HOST`: TrueNAS hostname or IP
- `API_USERNAME`: TrueNAS API username
- `API_PASSWORD`: TrueNAS API password
- `VNC_PASSWORD`: SPICE display password

### setup_logging()

```python
setup_logging(level: str = "INFO") -> None
```

Configures application logging.

**Parameters:**
- `level` (str): Logging level ("DEBUG", "INFO", "WARNING", "ERROR")

---

## Exceptions

### TrueNASError

```python
class TrueNASError(Exception):
    """Custom exception for TrueNAS API errors."""
```

Base exception class for all TrueNAS VM Manager errors.

**Common Scenarios:**
- API connection failures
- Authentication errors
- VM creation/deletion failures
- Template loading errors
- Device creation errors

---

## Usage Patterns

### Basic VM Creation

```python
from truenas_vm_manager import VMManager, TemplateManager, load_configuration

# Load configuration
config = load_configuration("config.yaml")

# Create template manager
template_manager = TemplateManager()

# Create VMs
with VMManager(host, user, pwd, vnc_pwd, template_manager) as vm_manager:
    vm_manager.create_vm_type(config, "controlplane", 5910)
    vm_manager.create_vm_type(config, "worker", 5920)
```

### Custom Template Directory

```python
from pathlib import Path

# Use custom template directory
template_manager = TemplateManager(Path("/custom/templates"))
```

### Error Handling

```python
try:
    with VMManager(host, user, pwd, vnc_pwd) as vm_manager:
        vm_manager.create_vm_type(config, "controlplane", 5910)
except TrueNASError as e:
    logger.error("VM creation failed: %s", e)
except Exception as e:
    logger.error("Unexpected error: %s", e)
```

### Configuration Validation

```python
try:
    config = load_configuration("config.yaml")
    # Configuration is valid
except ValueError as e:
    print(f"Configuration error: {e}")
except FileNotFoundError:
    print("Configuration file not found")
```

---

## TrueNAS API Integration

The VM Manager integrates with the following TrueNAS API endpoints:

### Authentication
- `auth.login` - User authentication
- `auth.logout` - Session cleanup

### VM Management
- `vm.create` - Create new VM
- `vm.start` - Start VM
- `vm.poweroff` - Power off VM
- `vm.delete` - Delete VM and optionally ZVOLs
- `vm.query` - List existing VMs

### Device Management
- `vm.device.create` - Add device to VM

### API Response Format

VM creation returns:
```json
{
  "id": 123,
  "name": "controlplane01",
  "status": {...}
}
```

Device creation returns:
```json
{
  "id": 456,
  "vm": 123,
  "dtype": "DISK",
  "attributes": {...}
}
```

---

## Thread Safety

The VM Manager is **not thread-safe**. Each thread should use its own `VMManager` instance if parallel VM creation is required.

## Performance Notes

- **Template Loading**: Templates are loaded once at startup
- **API Connections**: Single connection per VMManager instance
- **Memory Usage**: Templates are deep-copied for each use
- **Batch Operations**: Multiple VMs created in single API session