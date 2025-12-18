# Local Data Platform - Windows Setup Script
# PowerShell script for setting up LDP on Windows

$ErrorActionPreference = "Stop"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Local Data Platform - Initial Setup (Windows)" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if command exists
function Test-Command {
    param($Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

$missingTools = @()

if (-not (Test-Command "minikube")) {
    $missingTools += "minikube"
}
if (-not (Test-Command "kubectl")) {
    $missingTools += "kubectl"
}
if (-not (Test-Command "terraform")) {
    $missingTools += "terraform"
}
if (-not (Test-Command "helm")) {
    $missingTools += "helm"
}

if ($missingTools.Count -gt 0) {
    Write-Host ""
    Write-Host "ERROR: The following tools are not installed:" -ForegroundColor Red
    foreach ($tool in $missingTools) {
        Write-Host "  - $tool" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Installation options:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Option 1 - Using Chocolatey (recommended):" -ForegroundColor Cyan
    Write-Host "  choco install minikube kubectl terraform kubernetes-helm" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 2 - Using winget:" -ForegroundColor Cyan
    Write-Host "  winget install Kubernetes.minikube" -ForegroundColor White
    Write-Host "  winget install Kubernetes.kubectl" -ForegroundColor White
    Write-Host "  winget install Hashicorp.Terraform" -ForegroundColor White
    Write-Host "  winget install Helm.Helm" -ForegroundColor White
    Write-Host ""
    Write-Host "See docs/platform-guides/windows.md for detailed installation instructions" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ All prerequisites are installed" -ForegroundColor Green

# Check if Minikube is running
Write-Host ""
Write-Host "Checking Minikube status..." -ForegroundColor Yellow

try {
    $minikubeStatus = minikube status 2>$null
    $isRunning = $LASTEXITCODE -eq 0
} catch {
    $isRunning = $false
}

if (-not $isRunning) {
    Write-Host "Starting Minikube..." -ForegroundColor Yellow
    Write-Host "This may take several minutes on first run..." -ForegroundColor Gray

    minikube start `
        --cpus=4 `
        --memory=8192 `
        --disk-size=50g `
        --kubernetes-version=v1.34.0 `
        --driver=hyperv

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: Failed to start Minikube" -ForegroundColor Red
        Write-Host "Try running with Docker Desktop instead:" -ForegroundColor Yellow
        Write-Host "  minikube start --driver=docker --cpus=4 --memory=8192" -ForegroundColor White
        exit 1
    }

    # Enable addons
    Write-Host "Enabling Minikube addons..." -ForegroundColor Yellow
    minikube addons enable storage-provisioner
    minikube addons enable default-storageclass
    minikube addons enable metrics-server

    Write-Host "✓ Minikube started successfully" -ForegroundColor Green
} else {
    Write-Host "✓ Minikube is already running" -ForegroundColor Green
}

# Verify cluster
Write-Host ""
Write-Host "Verifying Kubernetes cluster..." -ForegroundColor Yellow
kubectl cluster-info

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Deploy the platform: " -NoNewline; Write-Host ".\scripts\windows\start.ps1" -ForegroundColor White
Write-Host "  2. Check health: " -NoNewline; Write-Host ".\scripts\windows\check-health.ps1" -ForegroundColor White
Write-Host ""
