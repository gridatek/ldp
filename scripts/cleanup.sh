#!/bin/bash
# Complete cleanup of Local Data Platform

set -e

echo "======================================"
echo "Local Data Platform - Cleanup"
echo "======================================"

read -p "This will remove all resources and stop Minikube. Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

# Change to project root
cd "$(dirname "$0")/.."

# Destroy Terraform resources
if [ -d "terraform/.terraform" ]; then
    echo "Destroying Terraform resources..."
    cd terraform
    terraform destroy -auto-approve || true
    cd ..
fi

# Delete namespace manually if it still exists
echo "Deleting Kubernetes namespace..."
kubectl delete namespace ldp --ignore-not-found=true

# Stop and delete Minikube
echo "Stopping and deleting Minikube..."
minikube stop || true
minikube delete || true

echo ""
echo "Cleanup completed successfully"
