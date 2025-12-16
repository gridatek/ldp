#!/bin/bash
# Initial setup script for Local Data Platform

set -e

echo "======================================"
echo "Local Data Platform - Initial Setup"
echo "======================================"

# Check prerequisites
echo "Checking prerequisites..."

command -v minikube >/dev/null 2>&1 || { echo "Error: minikube is not installed" >&2; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "Error: kubectl is not installed" >&2; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo "Error: terraform is not installed" >&2; exit 1; }
command -v helm >/dev/null 2>&1 || { echo "Error: helm is not installed" >&2; exit 1; }

echo "✓ All prerequisites are installed"

# Start Minikube if not running
if ! minikube status &>/dev/null; then
    echo "Starting Minikube..."
    minikube start \
        --cpus=4 \
        --memory=8192 \
        --disk-size=50g \
        --kubernetes-version=v1.34.0

    # Enable addons
    minikube addons enable storage-provisioner
    minikube addons enable default-storageclass
    minikube addons enable metrics-server

    echo "✓ Minikube started successfully"
else
    echo "✓ Minikube is already running"
fi

# Verify cluster
echo "Verifying Kubernetes cluster..."
kubectl cluster-info

echo ""
echo "Setup completed successfully!"
echo "Run './scripts/start.sh' to deploy the platform"
