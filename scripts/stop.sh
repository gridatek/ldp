#!/bin/bash
# Stop the Local Data Platform services

set -e

echo "======================================"
echo "Stopping Local Data Platform"
echo "======================================"

# Change to project root
cd "$(dirname "$0")/.."

# Destroy Terraform resources
echo "Destroying platform resources..."
cd terraform
terraform destroy -auto-approve
cd ..

echo ""
echo "Platform stopped successfully"
echo "Minikube is still running. To stop Minikube, run: minikube stop"
