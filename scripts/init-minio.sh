#!/bin/bash
# Initialize MinIO buckets and structure

set -e

echo "======================================"
echo "Initializing MinIO Buckets"
echo "======================================"

# Apply the Kubernetes job
kubectl apply -f kubernetes/jobs/init-minio-buckets.yaml

echo "Waiting for MinIO initialization to complete..."
kubectl wait --for=condition=complete \
    job/init-minio-buckets \
    -n ldp \
    --timeout=300s

echo "✓ MinIO buckets initialized successfully"

# Show job logs
echo ""
echo "Job logs:"
kubectl logs -n ldp job/init-minio-buckets
