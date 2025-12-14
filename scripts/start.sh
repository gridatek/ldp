#!/bin/bash
# Start and deploy the Local Data Platform

set -e

echo "======================================"
echo "Local Data Platform - Deployment"
echo "======================================"

# Change to project root
cd "$(dirname "$0")/.."

# Initialize Terraform if needed
if [ ! -d "terraform/.terraform" ]; then
    echo "Initializing Terraform..."
    cd terraform
    terraform init
    cd ..
fi

# Apply Terraform configuration
echo "Deploying platform with Terraform..."
cd terraform
terraform apply -auto-approve

echo ""
echo "Waiting for all pods to be ready..."
kubectl wait --for=condition=ready pod \
    --all \
    -n ldp \
    --timeout=600s || true

# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

echo ""
echo "======================================"
echo "Deployment Complete!"
echo "======================================"
echo ""
echo "Service URLs:"
echo "  Airflow UI:      http://${MINIKUBE_IP}:30080"
echo "    Username: admin"
echo "    Password: admin"
echo ""
echo "  MinIO Console:   http://${MINIKUBE_IP}:30901"
echo "    Username: admin"
echo "    Password: minioadmin"
echo ""
echo "  Spark Master UI: http://${MINIKUBE_IP}:30707"
echo ""
echo "  Jupyter:         http://${MINIKUBE_IP}:30888"
echo "    Check token: kubectl logs -n ldp deployment/jupyter"
echo ""
echo "Run './scripts/check-health.sh' to verify all services"
