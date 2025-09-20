# Troubleshooting Guide

This guide covers common issues and their solutions when using TrueNAS VM Manager.

## Table of Contents

- [Connection Issues](#connection-issues)
- [Authentication Problems](#authentication-problems)
- [Configuration Errors](#configuration-errors)
- [Template Issues](#template-issues)
- [VM Creation Failures](#vm-creation-failures)
- [Storage Problems](#storage-problems)
- [Network Issues](#network-issues)
- [Performance Issues](#performance-issues)
- [Environment Problems](#environment-problems)

---

## Connection Issues

### Error: Connection refused

```
Error: Connection failed: [Errno 111] Connection refused
```

**Possible Causes:**
- TrueNAS system is not running
- API service is disabled
- Firewall blocking connections
- Wrong hostname/IP address

**Solutions:**

1. **Verify TrueNAS is reachable:**
   ```bash
   ping 192.168.1.100
   telnet 192.168.1.100 80
   ```

2. **Check TrueNAS API service:**
   - Navigate to System → Services in TrueNAS web interface
   - Ensure "API" service is running
   - Restart the service if necessary

3. **Verify API endpoint:**
   ```bash
   curl -I http://192.168.1.100/api/current
   ```

4. **Check firewall rules:**
   - Ensure port 80/443 is open
   - Verify no local firewall blocking connections

### Error: Connection timeout

```
Error: Connection failed: [Errno 110] Connection timed out
```

**Solutions:**

1. **Network connectivity:**
   ```bash
   traceroute 192.168.1.100
   nslookup truenas.local
   ```

2. **TrueNAS network configuration:**
   - Check TrueNAS network settings
   - Verify correct VLAN configuration
   - Ensure network interface is up

3. **Update environment:**
   ```env
   TRUENAS_HOST=192.168.1.100  # Use IP instead of hostname
   ```

---

## Authentication Problems

### Error: Authentication failed

```
Error: Authentication failed
```

**Solutions:**

1. **Verify credentials:**
   ```bash
   # Test with TrueNAS web interface
   # Use same username/password
   ```

2. **Check user permissions