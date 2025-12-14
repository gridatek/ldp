#!/bin/bash
# Port forwarding helper for Local Data Platform services

set -e

SERVICE=${1:-""}

if [ -z "$SERVICE" ]; then
    echo "Usage: $0 <service>"
    echo ""
    echo "Available services:"
    echo "  airflow    - Airflow web UI (http://localhost:8080)"
    echo "  minio      - MinIO console (http://localhost:9001)"
    echo "  spark      - Spark master UI (http://localhost:8080)"
    echo "  jupyter    - Jupyter notebook (http://localhost:8888)"
    echo "  postgres   - PostgreSQL (localhost:5432)"
    exit 1
fi

case "$SERVICE" in
    airflow)
        echo "Port forwarding Airflow (http://localhost:8080)..."
        kubectl port-forward -n ldp svc/airflow-webserver 8080:8080
        ;;
    minio)
        echo "Port forwarding MinIO Console (http://localhost:9001)..."
        kubectl port-forward -n ldp svc/minio-console 9001:9001
        ;;
    spark)
        echo "Port forwarding Spark Master UI (http://localhost:8080)..."
        kubectl port-forward -n ldp svc/spark-master-svc 8080:8080
        ;;
    jupyter)
        echo "Port forwarding Jupyter (http://localhost:8888)..."
        kubectl port-forward -n ldp svc/jupyter 8888:8888
        ;;
    postgres)
        echo "Port forwarding PostgreSQL (localhost:5432)..."
        kubectl port-forward -n ldp svc/postgresql 5432:5432
        ;;
    *)
        echo "Unknown service: $SERVICE"
        exit 1
        ;;
esac
