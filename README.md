# TrueNAS VM Manager

A Python-based tool for automated creation and management of virtual machines on TrueNAS systems. This tool provides a template-driven approach to VM provisioning with support for different VM types and comprehensive device management.

## 🚀 Features

- ✅ **Template-based VM Creation** - JSON templates for consistent VM configuration
- ✅ **Multi-VM Type Support** - Separate configurations for controlplane and worker nodes
- ✅ **Configurable Storage** - Flexible ZVOL pool paths and ISO management
- ✅ **Automated Device Management** - Disk, network, display, and CDROM device provisioning
- ✅ **SPICE Display Integration** - Remote desktop access with configurable resolution
- ✅ **Network Bridge Support** - Multiple network interfaces with VIRTIO drivers
- ✅ **Error Recovery** - Automatic cleanup on VM creation failures
- ✅ **Configurable Logging** - Debug and monitoring capabilities
- ✅ **Environment-based Configuration** - Secure credential management

## 📋 Prerequisites

- **Python 3.8+** (Python 3.9+ recommended)
- **TrueNAS SCALE** with API enabled
- **Git** for dependency installation
- **Network access** to TrueNAS system
- **Sufficient storage** in configured ZVOL pool

## 🏗️ Project Structure

```
truenas-vm-manager/
├── README.md                 # This file
├── LICENSE                   # GNU LGPL v3 license
├── CHANGELOG.md             # Version history
├── CONTRIBUTING.md          # Contribution guidelines
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── truenas-vm-manager.py   # Main application
├── config.yaml             # VM configuration
├── docs/                   # Documentation
│   ├── ARCHITECTURE.md     # System architecture
│   ├── API.md             # API reference
│   ├── TROUBLESHOOTING.md # Common issues and solutions
│   └── EXAMPLES.md        # Usage examples
├── templates/             # JSON templates
│   ├── vms/
│   │   └── vm.json        # VM base template
│   └── devices/
│       ├── disk.json      # Disk device template
│       ├── nic.json       # Network interface template
│       ├── display.json   # SPICE display template
│       └── cdrom.json     # CDROM device template
└── .vscode/              # VS Code configuration
    └── launch.json       # Debug configuration
```

## ⚡ Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-username/truenas-vm-manager.git
cd truenas-vm-manager

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configuration

Create your environment file from the template:

```bash
cp .env.example .env
```

Edit `.env` with your TrueNAS credentials:

```env
TRUENAS_HOST=192.168.1.100
API_USERNAME=admin
API_PASSWORD=your_secure_password
VNC_PASSWORD=spice_password
```

### 3. Configure VMs

Edit `config.yaml` to match your environment:

```yaml
# Storage configuration
storage:
  pool_path: "your-pool/VMs"                    # ZVOL pool path
  cdrom_path: "/mnt/your-pool/your-iso.iso"     # Boot ISO path

# VM configurations
controlplane:
  count: 3
  memory: 4096
  cpu: 4
  disk:
    system: 30
  network:
    system: br0

worker:
  count: 3
  memory: 4096
  cpu: 4
  disk:
    system: 30
    storage: 600
  network:
    system: br0
    storage: br1
```

### 4. Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Create VMs
python truenas-vm-manager.py create

# Destroy VMs
python truenas-vm-manager.py destroy

# Use custom configuration
python truenas-vm-manager.py create --config production.yaml --log-level DEBUG
```

## 📚 Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - System design and components
- **[API Reference](docs/API.md)** - Detailed API documentation
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Examples](docs/EXAMPLES.md)** - Usage examples and configurations

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TRUENAS_HOST` | TrueNAS server IP/hostname | `192.168.1.100` |
| `API_USERNAME` | TrueNAS API username | `admin` |
| `API_PASSWORD` | TrueNAS API password | `your_secure_password` |
| `VNC_PASSWORD` | SPICE display password | `spice_access_password` |

### Storage Configuration

The `storage` section in `config.yaml` defines paths for VM storage and boot media:

```yaml
storage:
  pool_path: "seagate/VMs"                     # Base path for ZVOL creation
  cdrom_path: "/mnt/seagate/ubuntu-server.iso" # ISO file for VM boot
```

### VM Types

Each VM type supports different configurations:

- **controlplane**: Kubernetes control plane nodes
- **worker**: Kubernetes worker nodes with additional storage

## 🚀 Advanced Usage

### Custom Templates

Templates are located in `templates/` directory and can be customized:

- `vms/vm.json` - Base VM configuration
- `devices/disk.json` - Storage device template
- `devices/nic.json` - Network interface template
- `devices/display.json` - SPICE display template
- `devices/cdrom.json` - CDROM device template

### Multiple Configurations

Use different configuration files for different environments:

```bash
# Development environment
python truenas-vm-manager.py create --config dev.yaml

# Production environment
python truenas-vm-manager.py create --config production.yaml

# Testing with debug logging
python truenas-vm-manager.py create --config test.yaml --log-level DEBUG
```

## 🐛 Troubleshooting

For common issues and solutions, see [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

### Quick Fixes

- **Connection issues**: Verify TrueNAS API is accessible and credentials are correct
- **Template errors**: Ensure all template files exist and contain valid JSON
- **Storage errors**: Check ZVOL pool exists and has sufficient space
- **Network errors**: Verify bridge interfaces exist in TrueNAS

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/your-username/truenas-vm-manager.git
cd truenas-vm-manager

# Create development environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install development tools
pip install black flake8 mypy pytest
```

## 📄 License

This project is licensed under the GNU Lesser General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-username/truenas-vm-manager/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/truenas-vm-manager/discussions)
- **TrueNAS**: [https://www.truenas.com/](https://www.truenas.com/)

## 📊 Status

![License](https://img.shields.io/badge/license-LGPL%20v3-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Platform](https://img.shields.io/badge/platform-TrueNAS%20SCALE-orange.svg)

---

**Made with ❤️ for the TrueNAS community**