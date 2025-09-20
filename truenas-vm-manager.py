#!/usr/bin/env python3
"""TrueNAS VM Manager - Create and manage VMs on TrueNAS systems."""

import argparse
import json
import logging
import os
import sys
from copy import deepcopy
from pathlib import Path
from typing import Dict, Any, Optional, List

from dotenv import load_dotenv
import yaml
from truenas_api_client import Client


class TrueNASError(Exception):
    """Custom exception for TrueNAS API errors."""
    pass


class TemplateManager:
    """Manages device templates loaded from JSON files."""
    
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path(__file__).parent
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load device templates from JSON files."""
        template_files = {
            "vm": self.base_path / "templates" / "vms" / "vm.json",
            "nic": self.base_path / "templates" / "devices" / "nic.json",
            "disk": self.base_path / "templates" / "devices" / "disk.json",
            "display": self.base_path / "templates" / "devices" / "display.json",
            "cdrom": self.base_path / "templates" / "devices" / "cdrom.json",
        }
        
        for template_name, template_path in template_files.items():
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    self.templates[template_name] = json.load(f)
            except FileNotFoundError as e:
                raise TrueNASError(f"Template file not found: {template_path}")
            except json.JSONDecodeError as e:
                raise TrueNASError(f"Invalid JSON in template file {template_path}: {e}")
    
    def create_vm_spec(self, name: str, cores: int, threads: int, memory: int) -> Dict[str, Any]:
        """Create VM specification from template."""
        vm_spec = deepcopy(self.templates["vm"])
        vm_spec.update({
            "name": name,
            "cores": cores,
            "threads": threads,
            "memory": memory
        })
        return vm_spec
    
    def create_display_device(self, vm_id: int, port: int, password: str) -> Dict[str, Any]:
        """Create VNC display device from template."""
        display = deepcopy(self.templates["display"])
        display["vm"] = vm_id
        display["attributes"]["port"] = port
        display["attributes"]["password"] = password
        return display
    
    def create_cdrom_device(self, vm_id: int, path: str) -> Dict[str, Any]:
        """Create CDROM device from template."""
        cdrom = deepcopy(self.templates["cdrom"])
        cdrom["vm"] = vm_id
        cdrom["attributes"]["path"] = path
        return cdrom
    
    def create_nic_device(self, vm_id: int, nic_attach: str, mac: str = None) -> Dict[str, Any]:
        """Create network interface device from template."""
        nic = deepcopy(self.templates["nic"])
        nic["vm"] = vm_id
        nic["attributes"]["nic_attach"] = nic_attach
        if mac:
            nic["attributes"]["mac"] = mac
        return nic
    
    def create_disk_device(self, vm_id: int, zvol_name: str, size_bytes: int) -> Dict[str, Any]:
        """Create disk device from template."""
        disk = deepcopy(self.templates["disk"])
        disk["vm"] = vm_id
        disk["attributes"]["zvol_name"] = zvol_name
        disk["attributes"]["zvol_volsize"] = size_bytes
        return disk


class VMManager:
    """Manages VM operations on TrueNAS."""
    
    def __init__(self, host: str, username: str, password: str, vnc_password: str, 
                 template_manager: TemplateManager = None):
        self.host = host
        self.username = username
        self.password = password
        self.vnc_password = vnc_password
        self.client: Optional[Client] = None
        self.logger = logging.getLogger(__name__)
        self.templates = template_manager or TemplateManager()
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def connect(self) -> None:
        """Establish connection to TrueNAS API."""
        try:
            self.client = Client(f"ws://{self.host}/api/current")
            if not self.client.call("auth.login", self.username, self.password):
                raise TrueNASError("Authentication failed")
            self.logger.info("Successfully connected to TrueNAS at %s", self.host)
        except Exception as e:
            raise TrueNASError(f"Connection failed: {e}")
    
    def disconnect(self) -> None:
        """Close connection to TrueNAS API."""
        if self.client:
            try:
                self.client.call("auth.logout")
                self.client.close()
                self.logger.info("Disconnected from TrueNAS")
            except Exception as e:
                self.logger.warning("Error during disconnect: %s", e)
    
    def _add_device(self, device: Dict[str, Any]) -> None:
        """Add a device to a VM."""
        try:
            self.client.call("vm.device.create", device)
            device_type = device.get("attributes", {}).get("dtype", "unknown")
            self.logger.info("Added device: %s", device_type)
        except Exception as e:
            device_type = device.get("attributes", {}).get("dtype", "unknown")
            raise TrueNASError(f"Failed to add device {device_type}: {e}")
    
    def _create_vm_devices(self, vm_id: int, vm_name: str, vm_config: Dict[str, Any], 
                          vnc_port: int, storage_config: Dict[str, Any]) -> None:
        """Create and attach devices to a VM."""
        # Display device
        display = self.templates.create_display_device(vm_id, vnc_port, self.vnc_password)
        self._add_device(display)
        
        # CDROM device
        cdrom_path = storage_config["cdrom_path"]
        cdrom = self.templates.create_cdrom_device(vm_id, cdrom_path)
        self._add_device(cdrom)
        
        # Network interfaces
        for nic_attach in vm_config["network"].values():
            nic = self.templates.create_nic_device(vm_id, nic_attach)
            self._add_device(nic)
        
        # Storage devices
        storage_pool_path = storage_config["pool_path"]
        for disk_idx, size_gb in enumerate(vm_config["disk"].values()):
            size_bytes = size_gb * (1024 ** 3)  # Convert GB to bytes
            zvol_name = f"{storage_pool_path}/{vm_name}-disk{disk_idx}"
            disk = self.templates.create_disk_device(vm_id, zvol_name, size_bytes)
            self._add_device(disk)
    
    def create_vm_type(self, config: Dict[str, Any], vm_type: str, vnc_start_port: int) -> None:
        """Create VMs of a specific type."""
        vm_config = config.get(vm_type)
        storage_config = config.get("storage")
        
        if not vm_config:
            raise TrueNASError(f"VM type '{vm_type}' not found in configuration")
        
        if not storage_config:
            raise TrueNASError("Storage configuration not found in config")
        
        count = vm_config.get("count", 0)
        if count <= 0:
            self.logger.info("No VMs to create for type: %s", vm_type)
            return
        
        self.logger.info("Creating %d VM(s) of type: %s", count, vm_type)
        self.logger.info("Using storage pool path: %s", storage_config["pool_path"])
        self.logger.info("Using CDROM ISO path: %s", storage_config["cdrom_path"])
        
        for idx in range(count):
            vm_name = f"{vm_type}{idx + 1:02d}"
            vnc_port = vnc_start_port + idx + 1
            
            try:
                self._create_single_vm(vm_name, vm_config, vnc_port, storage_config)
            except TrueNASError as e:
                self.logger.error("Failed to create VM %s: %s", vm_name, e)
                continue
    
    def _create_single_vm(self, vm_name: str, vm_config: Dict[str, Any], vnc_port: int,
                         storage_config: Dict[str, Any]) -> None:
        """Create a single VM with all its devices."""
        # Create VM specification
        vm_spec = self.templates.create_vm_spec(
            name=vm_name,
            cores=vm_config["cpu"],
            threads=vm_config["cpu"],
            memory=vm_config["memory"]
        )
        
        # Create the VM
        try:
            response = self.client.call("vm.create", vm_spec)
            vm_id = response["id"]
            self.logger.info("Created VM: %s (ID: %s)", vm_name, vm_id)
        except Exception as e:
            raise TrueNASError(f"VM creation failed: {e}")
        
        try:
            # Add devices to the VM
            self._create_vm_devices(vm_id, vm_name, vm_config, vnc_port, storage_config)
            
            # Start the VM
            self.client.call("vm.start", vm_id)
            self.logger.info("Started VM: %s", vm_name)
            
        except Exception as e:
            # If device creation or startup fails, clean up the VM
            self.logger.error("Failed to configure VM %s, cleaning up: %s", vm_name, e)
            try:
                self.client.call("vm.delete", vm_id, {"zvols": True, "force": True})
            except Exception as cleanup_error:
                self.logger.error("Failed to clean up VM %s: %s", vm_name, cleanup_error)
            raise TrueNASError(f"VM configuration failed: {e}")
    
    def destroy_managed_vms(self, vm_prefixes: List[str] = None) -> None:
        """Destroy VMs with specific name prefixes."""
        if vm_prefixes is None:
            vm_prefixes = ["controlplane", "worker"]
        
        try:
            vms = self.client.call("vm.query")
        except Exception as e:
            raise TrueNASError(f"Failed to query VMs: {e}")
        
        managed_vms = [
            vm for vm in vms 
            if any(vm["name"].startswith(prefix) for prefix in vm_prefixes)
        ]
        
        if not managed_vms:
            self.logger.info("No managed VMs found to destroy")
            return
        
        self.logger.info("Found %d managed VM(s) to destroy", len(managed_vms))
        
        for vm in managed_vms:
            vm_id = vm["id"]
            vm_name = vm["name"]
            
            try:
                # Power off VM
                self.client.call("vm.poweroff", vm_id)
                self.logger.info("Powered off VM: %s", vm_name)
            except Exception as e:
                self.logger.warning("Failed to power off VM %s: %s", vm_name, e)
            
            try:
                # Delete VM and associated storage
                self.client.call("vm.delete", vm_id, {"zvols": True, "force": True})
                self.logger.info("Deleted VM: %s", vm_name)
            except Exception as e:
                self.logger.error("Failed to delete VM %s: %s", vm_name, e)


def load_configuration(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        # Validate configuration structure
        required_keys = ["storage", "controlplane", "worker"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration section: {key}")
        
        # Validate storage configuration
        storage_required_fields = ["pool_path", "cdrom_path"]
        for field in storage_required_fields:
            if field not in config["storage"]:
                raise ValueError(f"Missing required '{field}' in storage configuration")
        
        return config
        
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML configuration: {e}")


def setup_logging(level: str = "INFO") -> None:
    """Configure logging."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def get_environment_variables() -> tuple[str, str, str, str]:
    """Load and validate environment variables."""
    load_dotenv()
    
    truenas_host = os.environ.get("TRUENAS_HOST")
    api_username = os.environ.get("API_USERNAME")
    api_password = os.environ.get("API_PASSWORD")
    vnc_password = os.environ.get("VNC_PASSWORD")
    
    missing_vars = []
    if not truenas_host:
        missing_vars.append("TRUENAS_HOST")
    if not api_username:
        missing_vars.append("API_USERNAME")
    if not api_password:
        missing_vars.append("API_PASSWORD")
    if not vnc_password:
        missing_vars.append("VNC_PASSWORD")
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return truenas_host, api_username, api_password, vnc_password


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="TrueNAS VM Manager")
    parser.add_argument(
        "action", 
        choices=["create", "destroy"], 
        help="Action to perform"
    )
    parser.add_argument(
        "--config", 
        default="config.yaml", 
        help="Configuration file path (default: config.yaml)"
    )
    parser.add_argument(
        "--templates-dir", 
        default=None,
        help="Base directory for template files (default: script directory)"
    )
    parser.add_argument(
        "--log-level", 
        default="INFO", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        # Load environment variables
        truenas_host, api_username, api_password, vnc_password = get_environment_variables()
        
        # Load configuration
        config = load_configuration(args.config)
        
        # Initialize template manager
        templates_base_path = Path(args.templates_dir) if args.templates_dir else None
        template_manager = TemplateManager(templates_base_path)
        
        # Execute action
        with VMManager(truenas_host, api_username, api_password, vnc_password, 
                      template_manager) as vm_manager:
            if args.action == "create":
                vm_manager.create_vm_type(config, "controlplane", 5910)
                vm_manager.create_vm_type(config, "worker", 5920)
            elif args.action == "destroy":
                vm_manager.destroy_managed_vms()
        
        logger.info("Operation completed successfully")
        
    except (ValueError, TrueNASError, FileNotFoundError) as e:
        logger.error("Error: %s", e)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected error: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()