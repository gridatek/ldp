# LDP Setup Guide - macOS

Complete setup guide for running Local Data Platform on macOS.

## Prerequisites

### Required Software

- **macOS**: 11.0 (Big Sur) or later
- **Homebrew**: Package manager for macOS
- **At least 12GB RAM** and **60GB free disk space**

## Installation

### 1. Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Required Tools

```bash
# Install all required tools
brew install minikube kubectl terraform helm

# Verify installations
minikube version
kubectl version --client
terraform version
helm version
```

### 3. Install Docker Desktop (recommended)

Download and install from: https://www.docker.com/products/docker-desktop

Or using Homebrew:
```bash
brew install --cask docker
```

**Important**: Start Docker Desktop before proceeding.

### Alternative: HyperKit Driver

If you prefer not to use Docker Desktop:

```bash
# Install HyperKit
brew install hyperkit

# Use HyperKit as Minikube driver
minikube config set driver hyperkit
```

## Setup and Deployment

### 1. Clone the Repository

```bash
git clone https://github.com/gridatek/ldp.git
cd ldp
```

### 2. Run Setup

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run initial setup
./scripts/setup.sh
```

### 3. Deploy the Platform

```bash
./scripts/start.sh
```

This will take 10-15 minutes on first run.

### 4. Verify Deployment

```bash
# Check health
./scripts/check-health.sh

# Get Minikube IP
minikube ip
```

## Accessing Services

Get your Minikube IP:
```bash
minikube ip
```

Access services at:
- **Airflow UI**: `http://<minikube-ip>:30080` (admin/admin)
- **MinIO Console**: `http://<minikube-ip>:30901` (admin/minioadmin)
- **Spark Master**: `http://<minikube-ip>:30707`
- **Jupyter**: `http://<minikube-ip>:30888`

### Alternative: Port Forwarding

```bash
# Airflow
kubectl port-forward -n ldp svc/airflow-webserver 8080:8080

# MinIO
kubectl port-forward -n ldp svc/minio-console 9001:9001

# Then access at localhost:8080, localhost:9001, etc.
```

## macOS-Specific Tips

### Increase Docker Desktop Resources

1. Open Docker Desktop
2. Go to Settings → Resources
3. Increase:
   - CPUs to 4+
   - Memory to 8GB+
   - Disk to 60GB+

### Using Apple Silicon (M1/M2/M3)

LDP works on Apple Silicon, but note:
- Use Docker Desktop (recommended)
- Some images may need ARM64 variants
- Performance is excellent on M-series chips

```bash
# Start Minikube with more resources for M-series
minikube start \
  --cpus=6 \
  --memory=12288 \
  --disk-size=60g \
  --kubernetes-version=v1.34.0
```

### Troubleshooting on macOS

#### Minikube Won't Start

```bash
# Clean start
minikube delete
minikube start --driver=docker --cpus=4 --memory=8192
```

#### Pods Stuck in Pending

```bash
# Check resources
kubectl top nodes
minikube addons enable metrics-server
```

#### Port Already in Use

```bash
# Find and kill process using port
lsof -ti:8080 | xargs kill -9
```

### Performance Optimization

For better performance on macOS:

```bash
# Use VirtioFS for better file sharing
minikube start --driver=docker --mount --mount-string="$(pwd):/host"

# Enable more CPUs if available
minikube config set cpus 6
minikube config set memory 12288
```

## Using Makefile

macOS supports the Makefile commands:

```bash
# All make commands work
make setup
make start
make health
make stop
make cleanup
```

## Uninstallation

```bash
# Stop and remove all resources
make cleanup

# Or manually
./scripts/cleanup.sh

# Uninstall tools (optional)
brew uninstall minikube kubectl terraform helm
```

## Additional Resources

- [Docker Desktop for Mac](https://docs.docker.com/desktop/mac/)
- [Minikube macOS Guide](https://minikube.sigs.k8s.io/docs/drivers/docker/)
- [Homebrew Documentation](https://brew.sh/)

## Need Help?

- See [Troubleshooting Guide](../troubleshooting.md)
- Check [GitHub Issues](https://github.com/gridatek/ldp/issues)
