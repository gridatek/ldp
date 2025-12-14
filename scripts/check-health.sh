#!/bin/bash
# Health check script for Local Data Platform

set -e

echo "======================================"
echo "Local Data Platform - Health Check"
echo "======================================"

# Check if namespace exists
if ! kubectl get namespace ldp &>/dev/null; then
    echo "❌ Namespace 'ldp' does not exist"
    exit 1
fi

echo "✓ Namespace exists"
echo ""

# Check pods
echo "Pod Status:"
kubectl get pods -n ldp

echo ""

# Check if all pods are running
NOT_RUNNING=$(kubectl get pods -n ldp --field-selector=status.phase!=Running,status.phase!=Succeeded --no-headers 2>/dev/null | wc -l)

if [ "$NOT_RUNNING" -gt 0 ]; then
    echo "⚠️  Warning: $NOT_RUNNING pod(s) are not running"
else
    echo "✓ All pods are running"
fi

echo ""
echo "Services:"
kubectl get services -n ldp

echo ""
echo "Persistent Volume Claims:"
kubectl get pvc -n ldp

echo ""

# Check resource usage
echo "Resource Usage:"
kubectl top nodes 2>/dev/null || echo "Metrics not available (metrics-server may not be running)"
echo ""
kubectl top pods -n ldp 2>/dev/null || echo "Pod metrics not available"

echo ""
echo "======================================"
echo "Health check completed"
echo "======================================"
