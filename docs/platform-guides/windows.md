# LDP Setup Guide - Windows

Complete setup guide for running Local Data Platform on Windows.

## Prerequisites

### System Requirements

- **Windows**: 10/11 (64-bit)
- **Hyper-V** or **Docker Desktop**
- **At least 12GB RAM** and **60GB free disk space**
- **PowerShell**: 5.1 or later (built-in)

## Installation

### Method 1: Using Chocolatey (Recommended)

#### 1. Install Chocolatey

Open PowerShell as Administrator:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

#### 2. Install Required Tools

```powershell
# Install all tools at once
choco install minikube kubectl terraform kubernetes-helm -y

# Verify installations
minikube version
kubectl version --client
terraform version
helm version
```

### Method 2: Using winget

```powershell
# Windows Package Manager (built into Windows 11)
winget install Kubernetes.minikube
winget install Kubernetes.kubectl
winget install Hashicorp.Terraform
winget install Helm.Helm
```

### Method 3: Manual Installation

Download and install each tool:
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/)
- [Terraform](https://developer.hashicorp.com/terraform/install)
- [Helm](https://helm.sh/docs/intro/install/)

### 3. Install Docker Desktop

**Recommended for Windows 10/11:**

1. Download from: https://www.docker.com/products/docker-desktop
2. Install and restart your computer
3. Start Docker Desktop
4. Enable Kubernetes (optional, Minikube will handle this)

### Alternative: Enable Hyper-V

For Windows Pro/Enterprise without Docker Desktop:

```powershell
# Run as Administrator
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

Restart your computer after installation.

## Setup and Deployment

### 1. Clone the Repository

```powershell
git clone https://github.com/gridatek/ldp.git
cd ldp
```

### 2. Run Setup Script

Open PowerShell (no admin required):

```powershell
# Run initial setup
.\scripts\windows\setup.ps1
```

**If you get execution policy errors:**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Deploy the Platform

```powershell
.\scripts\windows\start.ps1
```

This will take 10-15 minutes on first run.

### 4. Verify Deployment

```powershell
# Check health
.\scripts\windows\check-health.ps1

# Get Minikube IP
minikube ip
```

## Accessing Services

Get your Minikube IP:
```powershell
minikube ip
```

Access services at:
- **Airflow UI**: `http://<minikube-ip>:30080` (admin/admin)
- **MinIO Console**: `http://<minikube-ip>:30901` (admin/minioadmin)
- **Spark Master**: `http://<minikube-ip>:30707`
- **Jupyter**: `http://<minikube-ip>:30888`

### Alternative: Port Forwarding

```powershell
# Airflow
kubectl port-forward -n ldp svc/airflow-webserver 8080:8080

# MinIO
kubectl port-forward -n ldp svc/minio-console 9001:9001

# Then access at http://localhost:8080, http://localhost:9001, etc.
```

## Windows-Specific Tips

### Choosing a Driver

**Docker Desktop (Recommended):**
```powershell
minikube config set driver docker
minikube start --cpus=4 --memory=8192
```

**Hyper-V:**
```powershell
# Requires administrator privileges
minikube config set driver hyperv
minikube start --cpus=4 --memory=8192
```

### Increase Docker Desktop Resources

1. Open Docker Desktop
2. Settings → Resources
3. Increase:
   - CPUs to 4+
   - Memory to 8GB+
   - Disk to 60GB+

### WSL2 Integration (Optional)

If using WSL2 with Docker Desktop:

1. Enable WSL2 integration in Docker Desktop settings
2. Install tools in WSL2 Ubuntu:
   ```bash
   sudo apt-get update
   sudo apt-get install -y kubectl
   ```
3. Use Linux scripts from WSL2

### Troubleshooting on Windows

#### Execution Policy Errors

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Hyper-V Not Available

Windows 10/11 Home doesn't include Hyper-V. Use Docker Desktop instead:
```powershell
minikube start --driver=docker
```

#### Minikube Won't Start

```powershell
# Clean start
minikube delete
minikube start --driver=docker --cpus=4 --memory=8192
```

#### VPN/Proxy Issues

```powershell
# Set proxy for Minikube
minikube start --docker-env HTTP_PROXY=http://proxy:port --docker-env HTTPS_PROXY=http://proxy:port
```

#### Antivirus Blocking

Some antivirus software blocks Minikube. Try:
1. Add Minikube folder to antivirus exceptions
2. Temporarily disable antivirus during setup

### Performance Optimization

```powershell
# Use more resources if available
minikube config set cpus 6
minikube config set memory 12288

# Enable caching
minikube start --cache-images
```

## Using PowerShell Scripts

All platform operations available via PowerShell:

```powershell
# Setup and deployment
.\scripts\windows\setup.ps1
.\scripts\windows\start.ps1

# Health check
.\scripts\windows\check-health.ps1

# Stop platform
.\scripts\windows\stop.ps1
```

## Makefile on Windows

**Option 1: Using Make for Windows**

Install with Chocolatey:
```powershell
choco install make
```

Then use standard make commands:
```powershell
make setup
make start
make health
```

**Option 2: Use PowerShell Scripts Instead**

PowerShell scripts provide the same functionality:
- `make setup` → `.\scripts\windows\setup.ps1`
- `make start` → `.\scripts\windows\start.ps1`
- `make health` → `.\scripts\windows\check-health.ps1`

## Uninstallation

```powershell
# Stop Minikube
minikube stop
minikube delete

# Uninstall tools (Chocolatey)
choco uninstall minikube kubectl terraform kubernetes-helm -y
```

## Additional Resources

- [Docker Desktop for Windows](https://docs.docker.com/desktop/windows/)
- [Minikube Windows Guide](https://minikube.sigs.k8s.io/docs/start/)
- [Chocolatey Documentation](https://chocolatey.org/docs)
- [Windows PowerShell Guide](https://docs.microsoft.com/en-us/powershell/)

## Need Help?

- See [Troubleshooting Guide](../troubleshooting.md)
- Check [GitHub Issues](https://github.com/gridatek/ldp/issues)
- Windows-specific issues: Tag with `windows` label
