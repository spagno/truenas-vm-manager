# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Cloud-init support for automated VM configuration
- Multi-TrueNAS support for distributed deployments
- VM snapshot and backup management
- GPU passthrough support
- Enhanced monitoring and health checks

## [1.0.0] - 2024-01-20

### 🎉 Initial Release

The first stable release of TrueNAS VM Manager - a Python-based tool for automated creation and management of virtual machines on TrueNAS SCALE systems.

### ✨ Features

#### Core Functionality
- **Template-based VM Creation** - JSON templates for consistent VM configuration
- **Multi-VM Type Support** - Separate configurations for controlplane and worker nodes
- **Configurable Storage Management** - Flexible ZVOL pool paths via `storage.pool_path`
- **Configurable ISO Management** - ISO file path configuration via `storage.cdrom_path`
- **Automated Device Management** - Disk, network, display, and CDROM device provisioning
- **SPICE Display Integration** - Remote desktop access with configurable resolution
- **Network Bridge Support** - Multiple network interfaces with VIRTIO drivers
- **Error Recovery** - Automatic cleanup on VM creation failures
- **Environment-based Configuration** - Secure credential management
- **Comprehensive Logging** - Debug and monitoring capabilities with configurable levels

#### VM Management
- **VMManager Class** - Complete VM lifecycle management with TrueNAS API integration
- **Context Manager Support** - Automatic connection management and cleanup
- **Batch Operations** - Efficient multi-VM creation and destruction
- **Sequential Naming** - Automatic VM naming (controlplane01, worker01, etc.)
- **Port Management** - Automatic SPICE display port assignment per VM type

#### Template System
- **TemplateManager Class** - JSON template loading and processing
- **VM Templates** - Base VM configuration with UEFI boot and secure boot
- **Device Templates** - Modular device configurations (disk, network, display, CDROM)
- **Template Validation** - Automatic validation of template structure and syntax
- **Deep Copy Safety** - Safe template usage preventing cross-contamination

#### Configuration Management
- **YAML Configuration** - Human-readable VM specifications
- **Environment Variables** - Secure credential storage outside codebase
- **Configuration Validation** - Automatic validation of required sections and fields
- **Storage Configuration** - Centralized storage and ISO path management

### 🏗️ Architecture

#### Core Components
- **VMManager** - VM operations and TrueNAS API interactions
- **TemplateManager** - Template loading and device configuration
- **Configuration Loader** - YAML parsing and validation
- **Error Handling** - Custom exceptions and recovery mechanisms

#### Storage Architecture
- **ZVOL Management** - Automatic creation with configurable pool paths
- **Naming Convention** - `{pool_path}/{vm_name}-disk{index}` pattern
- **Multi-disk Support** - System and storage disks per VM type
- **Automatic Cleanup** - ZVOL removal during VM destruction

#### Network Architecture
- **Bridge Attachment** - Support for multiple network bridges
- **VIRTIO Networking** - High-performance network virtualization
- **Multi-network VMs** - Different networks for system, storage, and management
- **Port Management** - Automatic SPICE port assignment (5911+, 5921+)

### 🔧 Supported VM Types

#### Controlplane VMs
- Kubernetes control plane nodes
- System disk only configuration
- Management network interface
- SPICE ports starting from 5911

#### Worker VMs
- Kubernetes worker nodes
- System + storage disk configuration
- Multiple network interfaces (system, storage)
- SPICE ports starting from 5921

### 📋 Requirements

#### System Requirements
- **Python 3.8+** (Python 3.9+ recommended)
- **TrueNAS SCALE** with API enabled
- **Git** for dependency installation
- **Network access** to TrueNAS system
- **Sufficient storage** in configured ZVOL pool

#### Dependencies
- `truenas_api_client` - TrueNAS API integration
- `python-dotenv` - Environment variable management
- `PyYAML` - YAML configuration parsing

### 🎯 Configuration

#### Environment Variables
```env
TRUENAS_HOST=192.168.1.100          # TrueNAS hostname or IP
API_USERNAME=admin                   # TrueNAS API username
API_PASSWORD=your_secure_password    # TrueNAS API password
VNC_PASSWORD=spice_password          # SPICE display password
```

#### Storage Configuration
```yaml
storage:
  pool_path: "seagate/VMs"                    # ZVOL pool base path
  cdrom_path: "/mnt/seagate/ubuntu-22.04.iso" # Boot ISO path
```

#### VM Type Configuration
```yaml
controlplane:
  count: 3        # Number of VMs
  memory: 4096    # RAM in MB
  cpu: 4          # CPU cores
  disk:
    system: 30    # System disk size in GB
  network:
    system: br68  # Network bridge

worker:
  count: 3
  memory: 4096
  cpu: 4
  disk:
    system: 30
    storage: 600  # Additional storage disk
  network:
    system: br68
    storage: br110
```

### 🔐 Security Features

- **Secure Boot** - UEFI secure boot enabled by default
- **Environment Variables** - No hardcoded credentials
- **API Authentication** - Secure WebSocket communication
- **Session Management** - Automatic connection cleanup
- **Permission Validation** - User privilege verification

### 🚀 Performance Features

- **Template Caching** - Templates loaded once and cached
- **Batch API Calls** - Multiple operations in single session
- **Error Isolation** - Individual VM failures don't affect others
- **Resource Optimization** - Efficient memory and CPU usage
- **VIRTIO Drivers** - High-performance virtualization

### 📚 Documentation

#### User Documentation
- **README.md** - Installation, configuration, and basic usage
- **docs/EXAMPLES.md** - Practical examples for different scenarios
- **docs/TROUBLESHOOTING.md** - Common issues and solutions

#### Developer Documentation
- **docs/ARCHITECTURE.md** - System design and components
- **docs/API.md** - Complete API reference
- **CONTRIBUTING.md** - Development guidelines and standards

### 🛠️ Command Line Interface

```bash
# Create VMs
python truenas-vm-manager.py create

# Destroy VMs
python truenas-vm-manager.py destroy

# Custom configuration
python truenas-vm-manager.py create --config production.yaml

# Debug mode
python truenas-vm-manager.py create --log-level DEBUG

# Custom templates
python truenas-vm-manager.py create --templates-dir ./custom-templates
```

### 📦 Project Structure

```
truenas-vm-manager/
├── README.md                 # Main documentation
├── LICENSE                   # GNU LGPL v3 license
├── CHANGELOG.md             # This file
├── CONTRIBUTING.md          # Contribution guidelines
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── truenas-vm-manager.py   # Main application
├── config.yaml             # Default configuration
├── docs/                   # Documentation
│   ├── ARCHITECTURE.md     # System architecture
│   ├── API.md             # API reference
│   ├── TROUBLESHOOTING.md # Issue resolution
│   └── EXAMPLES.md        # Usage examples
├── templates/             # JSON templates
│   ├── vms/vm.json        # VM base template
│   └── devices/           # Device templates
└── .vscode/              # Development configuration
```

### 🎯 Use Cases

#### Development Environment
- Single controlplane, single worker setup
- Minimal resource allocation for testing
- Fast deployment and cleanup cycles

#### Production Environment
- High-availability with 3+ controlplane nodes
- Multiple worker nodes for workload distribution
- Robust storage and network configuration

#### Multi-Environment
- Environment-specific configurations
- Isolated storage pools per environment
- Different resource allocations per environment

### ⚡ Quick Start

1. **Clone and setup**:
   ```bash
   git clone https://github.com/your-username/truenas-vm-manager.git
   cd truenas-vm-manager
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your TrueNAS details
   ```

3. **Create VMs**:
   ```bash
   python truenas-vm-manager.py create
   ```

### 🔮 Future Roadmap

#### Version 1.1.0 (Planned)
- Enhanced template customization
- VM state management (start/stop/restart)
- Resource monitoring and reporting
- Improved error recovery mechanisms

#### Version 1.2.0 (Planned)
- Cloud-init integration for automated OS configuration
- VM migration support between hosts
- Enhanced network configuration options
- Performance optimization improvements

#### Version 2.0.0 (Future)
- Multi-TrueNAS support for distributed deployments
- Web-based management interface
- API server mode for remote management
- Plugin system for extensibility

---

## Version History Summary

- **v1.0.0** - Initial release with complete VM management functionality

## Migration Instructions

### New Installation
This is the first release - no migration needed. Follow the installation instructions in README.md.

### From Development/Beta Versions
If you were using development versions:

1. **Backup existing configurations**
2. **Follow fresh installation steps**
3. **Migrate custom templates** to new structure
4. **Update configuration format** to match v1.0.0 structure

## Known Issues

### v1.0.0
- **Template Directory**: Defaul# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation structure
- API reference documentation
- Troubleshooting guide with common issues
- Usage examples for different scenarios
- Contributing guidelines for developers

### Changed
- Improved README with better structure and examples
- Enhanced project organization with docs/ directory

## [1.1.0] - 2024-01-20

### Added
- ✨ **Configurable Storage Paths** - Storage pool path now configurable via `storage.pool_path` in config.yaml
- ✨ **Configurable CDROM Path** - ISO file path now configurable via `storage.cdrom_path` in config.yaml
- 📝 Enhanced configuration validation for storage settings
- 🔍 Improved logging with storage and CDROM path information
- 📚 Updated documentation with storage configuration examples

### Changed
- 🔧 **Breaking Change**: config.yaml now requires `storage` section with `pool_path` and `cdrom_path`
- 🏗️ Refactored `_create_vm_devices()` method to accept storage configuration
- 🏗️ Updated `create_cdrom_device()` to require path parameter
- 📖 Updated README with new configuration structure

### Fixed
- 🐛 Improved error handling for missing storage configuration
- 🐛 Better validation of configuration file structure

### Migration Guide
To upgrade from v1.0.0, update your config.yaml:

```yaml
# Add this new storage section
storage:
  pool_path: "seagate/VMs"  # Your existing ZVOL pool path
  cdrom_path: "/mnt/seagate/metal-amd64.iso"  # Your ISO file path

# Rest of your configuration remains the same
controlplane:
  count: 3
  # ... existing config
```

## [1.0.0] - 2024-01-15

### Added
- 🎉 **Initial Release** of TrueNAS VM Manager
- ✅ **Template-based VM Creation** - JSON templates for consistent VM configuration
- ✅ **Multi-VM Type Support** - Separate configurations for controlplane and worker nodes
- ✅ **Automated Device Management** - Disk, network, display, and CDROM device provisioning
- ✅ **SPICE Display Integration** - Remote desktop access with configurable resolution
- ✅ **Network Bridge Support** - Multiple network interfaces with VIRTIO drivers
- ✅ **Storage Management** - Automatic ZVOL creation and management
- ✅ **Error Recovery** - Automatic cleanup on VM creation failures
- ✅ **Configurable Logging** - Debug and monitoring capabilities
- ✅ **Environment-based Configuration** - Secure credential management

### Core Features
- **VMManager Class** - Manages VM lifecycle and TrueNAS API interactions
- **TemplateManager Class** - Handles loading and processing of JSON templates
- **Configuration Management** - YAML-based configuration with validation
- **Command Line Interface** - Simple create/destroy operations
- **Context Manager Support** - Automatic resource cleanup

### Templates
- **VM Template** - Base VM configuration with UEFI boot and secure boot
- **Disk Template** - VIRTIO disk devices with automatic ZVOL creation
- **Network Template** - VIRTIO network interfaces with bridge support
- **Display Template** - SPICE display with configurable resolution and ports
- **CDROM Template** - ISO mounting for OS installation

### Supported VM Types
- **Controlplane VMs** - Kubernetes control plane nodes with system disk
- **Worker VMs** - Kubernetes worker nodes with system and storage disks
- **Automatic Naming** - Sequential naming (controlplane01, worker01, etc.)
- **Port Management** - Automatic SPICE port assignment per VM type

### Requirements
- Python 3.8+
- TrueNAS SCALE with API enabled
- Network access to TrueNAS system
- Sufficient storage in ZVOL pool

### Configuration
- Environment variables for secure credential storage
- YAML configuration for VM specifications
- JSON templates for device configurations
- Flexible memory, CPU, and storage allocation

### Documentation
- Comprehensive README with setup instructions
- Architecture documentation
- Troubleshooting guide
- Usage examples

---

## Version History Summary

- **v1.1.0** - Added configurable storage and CDROM paths
- **v1.0.0** - Initial release with core VM management functionality

## Upgrade Instructions

### From v1.0.0 to v1.1.0

1. **Backup your configuration**:
   ```bash
   cp config.yaml config.yaml.backup
   ```

2. **Update config.yaml structure**:
   ```yaml
   # Add storage section at the top
   storage:
     pool_path: "your-pool/VMs"
     cdrom_path: "/mnt/your-pool/your-iso.iso"
   
   # Keep existing controlplane and worker sections unchanged
   ```

3. **Test configuration**:
   ```bash
   python truenas-vm-manager.py --help
   ```

4. **Update templates if customized**:
   - No changes needed for default templates
   - Custom templates should continue working

## Known Issues

### v1.1.0
- None currently known

### v1.0.0
- Fixed in v1.1.0: Hardcoded storage paths limiting flexibility

## Contributors

Thank you to all contributors who helped make this project possible:

- **Initial Development** - Core VM management functionality
- **Configuration Enhancement** - Flexible storage configuration
- **Documentation** - Comprehensive guides and examples

## Breaking Changes

### v1.1.0
- **config.yaml structure change** - Added required `storage` section
- **Method signature change** - `create_cdrom_device()` now requires path parameter

### Migration Required
When upgrading to v1.1.0, you must update your configuration file structure. See the migration guide above for details.

## Security Updates

### v1.1.0
- Improved configuration validation prevents invalid storage paths
- Enhanced error handling for missing configuration sections

### v1.0.0
- Environment-based credential management
- No hardcoded passwords or sensitive information
- Secure API communication with TrueNAS

## Performance Improvements

### v1.1.0
- More efficient template loading with validation improvements
- Better error handling reduces retry overhead

### v1.0.0
- Template caching for improved performance
- Batch VM creation in single API session
- Automatic resource cleanup on failures

## Deprecations

### Future Considerations
- **v2.0.0** may include changes to template structure
- **v2.0.0** may modify API interfaces for better extensibility

Currently, no features are deprecated in v1.1.0.

---

## Links

- **GitHub Repository**: https://github.com/your-username/truenas-vm-manager
- **Documentation**: https://github.com/your-username/truenas-vm-manager/tree/main/docs
- **Issue Tracker**: https://github.com/your-username/truenas-vm-manager/issues
- **Releases**: https://github.com/your-username/truenas-vm-manager/releases