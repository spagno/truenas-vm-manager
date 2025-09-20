# Usage Examples

This document provides practical examples for using TrueNAS VM Manager in different scenarios.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Development Environment](#development-environment)
- [Production Environment](#production-environment)
- [Multi-Environment Setup](#multi-environment-setup)
- [Custom Storage Configurations](#custom-storage-configurations)
- [Network Configurations](#network-configurations)
- [Testing and Debugging](#testing-and-debugging)
- [Advanced Scenarios](#advanced-scenarios)

---

## Basic Usage

### Simple Kubernetes Cluster

**config.yaml:**
```yaml
storage:
  pool_path: "tank/kubernetes"
  cdrom_path: "/mnt/tank/ubuntu-22.04-server.iso"

controlplane:
  count: 1
  memory: 4096
  cpu: 4
  disk:
    system: 30
  network:
    system: br0

worker:
  count: 2
  memory: 8192
  cpu: 4
  disk:
    system: 30
    storage: 100
  network:
    system: br0
    storage: br1
```

**Commands:**
```bash
# Create the cluster
python truenas-vm-manager.py create

# Destroy when done
python truenas-vm-manager.py destroy
```

**Expected output:**
```
2024-01-20 10:30:15 [INFO] __main__: Successfully connected to TrueNAS at 192.168.1.100
2024-01-20 10:30:15 [INFO] __main__: Creating 1 VM(s) of type: controlplane
2024-01-20 10:30:15 [INFO] __main__: Using storage pool path: tank/kubernetes
2024-01-20 10:30:15 [INFO] __main__: Using CDROM ISO path: /mnt/tank/ubuntu-22.04-server.iso
2024-01-20 10:30:16 [INFO] __main__: Created VM: controlplane01 (ID: 1)
2024-01-20 10:30:17 [INFO] __main__: Added device: DISPLAY
2024-01-20 10:30:18 [INFO] __main__: Added device: CDROM
2024-01-20 10:30:19 [INFO] __main__: Added device: NIC
2024-01-20 10:30:20 [INFO] __main__: Added device: DISK
2024-01-20 10:30:21 [INFO] __main__: Started VM: controlplane01
```

---

## Development Environment

### Development Configuration

**dev.yaml:**
```yaml
storage:
  pool_path: "fast-ssd/dev-vms"
  cdrom_path: "/mnt/fast-ssd/debian-12-netinst.iso"

controlplane:
  count: 1
  memory: 2048  # Reduced for development
  cpu: 2
  disk:
    system: 20   # Smaller disk
  network:
    system: br-dev

worker:
  count: 1      # Single worker for dev
  memory: 2048
  cpu: 2
  disk:
    system: 20
    storage: 50  # Smaller storage
  network:
    system: br-dev
    storage: br-storage
```

**Usage:**
```bash
# Create development environment
python truenas-vm-manager.py create --config dev.yaml --log-level DEBUG

# Quick cleanup for testing
python truenas-vm-manager.py destroy --config dev.yaml
```

### Development with Custom Templates

**custom-templates/vms/dev-vm.json:**
```json
{
  "name": null,
  "vcpus": 1,
  "cores": null,
  "threads": null,
  "cpu_mode": "HOST-MODEL",
  "memory": null,
  "bootloader": "UEFI",
  "autostart": false,
  "enable_secure_boot": false,
  "time": "LOCAL",
  "shutdown_timeout": 30
}
```

**Commands:**
```bash
# Use custom templates
python truenas-vm-manager.py create --config dev.yaml --templates-dir ./custom-templates
```

---

## Production Environment

### High-Availability Cluster

**production.yaml:**
```yaml
storage:
  pool_path: "enterprise/kubernetes-prod"
  cdrom_path: "/mnt/enterprise/ubuntu-22.04-server.iso"

controlplane:
  count: 3      # HA setup
  memory: 8192  # More memory for production
  cpu: 6        # More CPU
  disk:
    system: 100 # Larger system disk
  network:
    system: br-prod

worker:
  count: 5      # More workers
  memory: 16384 # High memory for workloads
  cpu: 8
  disk:
    system: 100
    storage: 1000  # Large storage
  network:
    system: br-prod
    storage: br-storage-prod
```

**Production Deployment:**
```bash
# Verify configuration first
python -c "
from truenas_vm_manager import load_configuration
config = load_configuration('production.yaml')
print('✓ Configuration valid')
print(f'Total VMs: {config[\"controlplane\"][\"count\"] + config[\"worker\"][\"count\"]}')
print(f'Storage pool: {config[\"storage\"][\"pool_path\"]}')
"

# Deploy production cluster
python truenas-vm-manager.py create --config production.yaml

# Monitor creation
tail -f /var/log/truenas-vm-manager.log
```

### Production with Backup Storage

**production-backup.yaml:**
```yaml
storage:
  pool_path: "primary/kubernetes-prod"
  cdrom_path: "/mnt/primary/ubuntu-22.04-server.iso"

controlplane:
  count: 3
  memory: 8192
  cpu: 6
  disk:
    system: 100
    backup: 200   # Additional backup disk
  network:
    system: br-prod
    backup: br-backup

worker:
  count: 5
  memory: 16384
  cpu: 8
  disk:
    system: 100
    storage: 1000
    backup: 500
  network:
    system: br-prod
    storage: br-storage-prod
    backup: br-backup
```

---

## Multi-Environment Setup

### Directory Structure

```
environments/
├── dev.yaml
├── staging.yaml
├── production.yaml
└── testing.yaml

templates/
├── dev/
│   └── vms/vm.json
├── prod/
│   └── vms/vm.json
└── shared/
    └── devices/
```

### Environment-Specific Configurations

**environments/staging.yaml:**
```yaml
storage:
  pool_path: "staging/k8s-staging"
  cdrom_path: "/mnt/staging/ubuntu-staging.iso"

controlplane:
  count: 2
  memory: 6144
  cpu: 4
  disk:
    system: 50
  network:
    system: br-staging

worker:
  count: 3
  memory: 12288
  cpu: 6
  disk:
    system: 50
    storage: 500
  network:
    system: br-staging
    storage: br-storage-staging
```

**Deployment Script:**
```bash
#!/bin/bash
# deploy.sh

ENVIRONMENT=${1:-dev}
CONFIG_FILE="environments/${ENVIRONMENT}.yaml"
TEMPLATES_DIR="templates/${ENVIRONMENT}"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Configuration not found: $CONFIG_FILE"
    exit 1
fi

echo "🚀 Deploying $ENVIRONMENT environment..."
python truenas-vm-manager.py create \
    --config "$CONFIG_FILE" \
    --templates-dir "$TEMPLATES_DIR" \
    --log-level INFO

echo "✅ $ENVIRONMENT deployment complete"
```

**Usage:**
```bash
# Deploy different environments
./deploy.sh dev
./deploy.sh staging
./deploy.sh production
```

---

## Custom Storage Configurations

### Multiple Storage Pools

**multi-pool.yaml:**
```yaml
storage:
  pool_path: "nvme-fast/critical-vms"  # Fast storage for system
  cdrom_path: "/mnt/bulk-storage/isos/ubuntu-22.04.iso"

controlplane:
  count: 3
  memory: 8192
  cpu: 6
  disk:
    system: 50    # On fast NVMe
  network:
    system: br0

worker:
  count: 3
  memory: 16384
  cpu: 8
  disk:
    system: 50    # On fast NVMe
    storage: 1000 # Will be created on same pool
  network:
    system: br0
    storage: br1
```

### Different ISOs per VM Type

For different ISOs per VM type, you would need custom templates:

**templates/controlplane-devices/cdrom.json:**
```json
{
  "vm": null,
  "attributes": {
    "dtype": "CDROM",
    "path": "/mnt/storage/ubuntu-server-22.04.iso"
  },
  "order": 1003
}
```

**templates/worker-devices/cdrom.json:**
```json
{
  "vm": null,
  "attributes": {
    "dtype": "CDROM",
    "path": "/mnt/storage/ubuntu-minimal-22.04.iso"
  },
  "order": 1003
}
```

---

## Network Configurations

### Complex Network Setup

**network-complex.yaml:**
```yaml
storage:
  pool_path: "storage/network-test"
  cdrom_path: "/mnt/storage/network-os.iso"

controlplane:
  count: 3
  memory: 4096
  cpu: 4
  disk:
    system: 30
  network:
    management: br-mgmt    # Management network
    cluster: br-cluster    # Kubernetes cluster network
    external: br-external  # External access

worker:
  count: 5
  memory: 8192
  cpu: 6
  disk:
    system: 30
    storage: 500
  network:
    management: br-mgmt
    cluster: br-cluster
    storage: br-storage    # Dedicated storage network
    external: br-external
```

### VLAN Configuration

**vlan-setup.yaml:**
```yaml
storage:
  pool_path: "enterprise/vlan-cluster"
  cdrom_path: "/mnt/enterprise/os.iso"

controlplane:
  count: 3
  memory: 8192
  cpu: 6
  disk:
    system: 100
  network:
    vlan100: br-vlan100   # Management VLAN
    vlan200: br-vlan200   # Cluster VLAN

worker:
  count: 6
  memory: 16384
  cpu: 8
  disk:
    system: 100
    storage: 1000
  network:
    vlan100: br-vlan100   # Management VLAN
    vlan200: br-vlan200   # Cluster VLAN
    vlan300: br-vlan300   # Storage VLAN
```

---

## Testing and Debugging

### Minimal Test Configuration

**test.yaml:**
```yaml
storage:
  pool_path: "test-pool/debug"
  cdrom_path: "/mnt/test-pool/minimal.iso"

controlplane:
  count: 1
  memory: 1024  # Minimal memory
  cpu: 1        # Single CPU
  disk:
    system: 10  # Small disk
  network:
    system: br0

worker:
  count: 1
  memory: 1024
  cpu: 1
  disk:
    system: 10
    storage: 20
  network:
    system: br0
    storage: br1
```

**Debug Commands:**
```bash
# Test configuration validation
python -c "
from truenas_vm_manager import load_configuration
try:
    config = load_configuration('test.yaml')
    print('✅ Configuration valid')
except Exception as e:
    print(f'❌ Configuration error: {e}')
"

# Test template loading
python -c "
from truenas_vm_manager import TemplateManager
try:
    tm = TemplateManager()
    print('✅ Templates loaded')
except Exception as e:
    print(f'❌ Template error: {e}')
"

# Create with full debugging
python truenas-vm-manager.py create --config test.yaml --log-level DEBUG
```

### Step-by-Step Testing

**Create single VM for testing:**
```bash
# 1. Test connection only
python -c "
from truenas_vm_manager import VMManager, get_environment_variables
host, user, pwd, vnc = get_environment_variables()
try:
    with VMManager(host, user, pwd, vnc) as vm:
        print('✅ Connection successful')
except Exception as e:
    print(f'❌ Connection failed: {e}')
"

# 2. Test with minimal config
python truenas-vm-manager.py create --config test.yaml

# 3. Clean up
python truenas-vm-manager.py destroy --config test.yaml
```

---

## Advanced Scenarios

### Large Scale Deployment

**large-scale.yaml:**
```yaml
storage:
  pool_path: "enterprise/large-k8s"
  cdrom_path: "/mnt/enterprise/ubuntu-optimized.iso"

controlplane:
  count: 5      # Large HA setup
  memory: 16384 # High memory
  cpu: 12       # Many cores
  disk:
    system: 200
    etcd: 100   # Separate etcd storage
  network:
    cluster: br-cluster
    storage: br-storage
    management: br-mgmt

worker:
  count: 20     # Many workers
  memory: 32768 # Very high memory
  cpu: 16       # Many cores
  disk:
    system: 200
    storage: 2000
    cache: 500  # Cache storage
  network:
    cluster: br-cluster
    storage: br-storage
    management: br-mgmt
```

**Staged deployment:**
```bash
#!/bin/bash
# large-scale-deploy.sh

echo "🚀 Large scale deployment starting..."

# Deploy in batches to avoid resource contention
echo "📦 Deploying controlplane nodes..."
python truenas-vm-manager.py create --config large-scale.yaml

# Wait for controlplane to be ready
echo "⏳ Waiting for controlplane to initialize..."
sleep 300

# Deploy workers in batches
echo "📦 Deploying worker nodes..."
# Note: In practice, you might modify the script to deploy workers in smaller batches

echo "✅ Large scale deployment complete"
echo "🔍 Verifying VMs..."
# Add verification logic here
```

### Mixed Workload Environment

**mixed-workloads.yaml:**
```yaml
storage:
  pool_path: "hybrid/mixed-env"
  cdrom_path: "/mnt/hybrid/multi-purpose.iso"

# Web tier
controlplane:
  count: 2
  memory: 8192
  cpu: 6
  disk:
    system: 100
    app: 200
  network:
    web: br-web
    internal: br-internal

# Database tier (using worker config)
worker:
  count: 3
  memory: 32768  # High memory for databases
  cpu: 16
  disk:
    system: 100
    database: 1000  # Large database storage
    logs: 200       # Separate log storage
  network:
    internal: br-internal
    storage: br-storage
    backup: br-backup
```

### GPU-Enabled VMs

For GPU passthrough, you'd need custom templates:

**templates/gpu-devices/gpu.json:**
```json
{
  "vm": null,
  "attributes": {
    "dtype": "PCI",
    "pptdev": "pci_0000_01_00_0"
  },
  "order": 1005
}
```

**gpu-compute.yaml:**
```yaml
storage:
  pool_path: "nvme/gpu-cluster"
  cdrom_path: "/mnt/nvme/ubuntu-cuda.iso"

controlplane:
  count: 3
  memory: 8192
  cpu: 8
  disk:
    system: 100
  network:
    cluster: br-cluster

worker:
  count: 4
  memory: 65536  # High memory for GPU workloads
  cpu: 16
  disk:
    system: 200
    storage: 2000
    scratch: 1000  # Fast scratch storage
  network:
    cluster: br-cluster
    storage: br-storage
    gpu: br-gpu-fabric  # High-speed GPU interconnect
```

---

## Performance Optimization Examples

### Optimized for Speed

**fast-deployment.yaml:**
```yaml
storage:
  pool_path: "nvme-raid/fast-vms"     # Fast NVMe RAID
  cdrom_path: "/mnt/nvme-raid/minimal-os.iso"  # Minimal OS

controlplane:
  count: 3
  memory: 4096
  cpu: 4
  disk:
    system: 30    # Reasonable size for speed
  network:
    system: br0   # Single network for simplicity

worker:
  count: 3
  memory: 8192
  cpu: 6
  disk:
    system: 30
    storage: 200  # Moderate storage
  network:
    system: br0
    storage: br1
```

### Optimized for Resources

**resource-efficient.yaml:**
```yaml
storage:
  pool_path: "bulk/efficient-vms"
  cdrom_path: "/mnt/bulk/alpine-minimal.iso"  # Very small OS

controlplane:
  count: 1      # Minimal HA
  memory: 2048  # Conservative memory
  cpu: 2
  disk:
    system: 15  # Small system partition
  network:
    system: br0

worker:
  count: 2
  memory: 4096
  cpu: 4
  disk:
    system: 15
    storage: 100
  network:
    system: br0
    storage: br1
```

These examples demonstrate the flexibility of TrueNAS VM Manager for various deployment scenarios, from simple development setups to complex production environments.