.PHONY: help setup start stop cleanup health test init-minio port-forward troubleshoot

# Default target
help:
	@echo "Local Data Platform - Make Commands"
	@echo ""
	@echo "Setup & Deployment:"
	@echo "  make setup       - Initial setup (start Minikube, enable addons)"
	@echo "  make start       - Deploy the platform using Terraform"
	@echo "  make stop        - Stop the platform (destroy Terraform resources)"
	@echo "  make cleanup     - Complete cleanup (remove all resources and Minikube)"
	@echo ""
	@echo "Operations:"
	@echo "  make health      - Check health of all services"
	@echo "  make init-minio  - Initialize MinIO buckets"
	@echo "  make logs        - Show logs for all pods"
	@echo "  make pods        - List all pods in ldp namespace"
	@echo "  make services    - List all services"
	@echo ""
	@echo "Troubleshooting:"
	@echo "  make troubleshoot      - Run quick diagnostics"
	@echo "  make troubleshoot-full - Run full diagnostic check"
	@echo "  make export-logs       - Export all logs to ./logs/"
	@echo "  make events            - Show recent Kubernetes events"
	@echo ""
	@echo "Monitoring:"
	@echo "  make import-dashboards - Import Grafana dashboards"
	@echo ""
	@echo "Port Forwarding:"
	@echo "  make airflow-forward   - Forward Airflow UI (localhost:8080)"
	@echo "  make minio-forward     - Forward MinIO Console (localhost:9001)"
	@echo "  make spark-forward     - Forward Spark UI (localhost:8080)"
	@echo "  make jupyter-forward   - Forward Jupyter (localhost:8888)"
	@echo "  make postgres-forward  - Forward PostgreSQL (localhost:5432)"
	@echo "  make grafana-forward   - Forward Grafana (localhost:3000)"
	@echo "  make prometheus-forward - Forward Prometheus (localhost:9090)"
	@echo ""
	@echo "Testing:"
	@echo "  make test        - Run all tests"
	@echo "  make test-unit   - Run unit tests"
	@echo "  make test-int    - Run integration tests"
	@echo ""
	@echo "Development:"
	@echo "  make tf-init     - Initialize Terraform"
	@echo "  make tf-plan     - Plan Terraform changes"
	@echo "  make tf-apply    - Apply Terraform changes"
	@echo "  make minikube-ip - Show Minikube IP address"
	@echo "  make load-examples - Copy example code for demo/testing"

# Setup & Deployment
setup:
	@./scripts/setup.sh

start:
	@./scripts/start.sh

stop:
	@./scripts/stop.sh

cleanup:
	@./scripts/cleanup.sh

# Operations
health:
	@./scripts/check-health.sh

init-minio:
	@./scripts/init-minio.sh

logs:
	@kubectl logs -n ldp --all-containers=true --tail=100 -l app.kubernetes.io/instance=airflow

pods:
	@kubectl get pods -n ldp

services:
	@kubectl get services -n ldp

pvc:
	@kubectl get pvc -n ldp

# Port Forwarding
airflow-forward:
	@./scripts/port-forward.sh airflow

minio-forward:
	@./scripts/port-forward.sh minio

spark-forward:
	@./scripts/port-forward.sh spark

jupyter-forward:
	@./scripts/port-forward.sh jupyter

postgres-forward:
	@./scripts/port-forward.sh postgres

grafana-forward:
	@echo "Port forwarding Grafana (http://localhost:3000)..."
	@kubectl port-forward -n ldp svc/grafana 3000:3000

prometheus-forward:
	@echo "Port forwarding Prometheus (http://localhost:9090)..."
	@kubectl port-forward -n ldp svc/prometheus 9090:9090

# Troubleshooting
troubleshoot:
	@./scripts/troubleshoot.sh --quick

troubleshoot-full:
	@./scripts/troubleshoot.sh --full

export-logs:
	@./scripts/troubleshoot.sh --export-logs

events:
	@kubectl get events -n ldp --sort-by='.lastTimestamp' | tail -30

logs-airflow:
	@kubectl logs -n ldp -l component=webserver --tail=100 -f

logs-scheduler:
	@kubectl logs -n ldp -l component=scheduler --tail=100 -f

logs-spark:
	@kubectl logs -n ldp -l app=spark-master --tail=100 -f

logs-minio:
	@kubectl logs -n ldp -l app=minio --tail=100 -f

# Monitoring
import-dashboards:
	@./monitoring/import-dashboards.sh

# Testing
test: test-unit test-int

test-unit:
	@echo "Running unit tests..."
	@pytest airflow/tests/ spark/tests/ -v

test-int:
	@echo "Running integration tests..."
	@pytest tests/integration/ -v

test-e2e:
	@echo "Running end-to-end tests..."
	@pytest tests/e2e/ -v

# Terraform
tf-init:
	@cd terraform && terraform init

tf-plan:
	@cd terraform && terraform plan

tf-apply:
	@cd terraform && terraform apply

tf-destroy:
	@cd terraform && terraform destroy

# Utilities
minikube-ip:
	@minikube ip

minikube-dashboard:
	@minikube dashboard

describe-pod:
	@read -p "Enter pod name: " pod; kubectl describe pod $$pod -n ldp

exec-pod:
	@read -p "Enter pod name: " pod; kubectl exec -it $$pod -n ldp -- /bin/bash

# Docker builds
build-airflow:
	@docker build -t ldp-airflow:latest -f docker/airflow/Dockerfile .

build-spark:
	@docker build -t ldp-spark:latest -f docker/spark/Dockerfile .

build-jupyter:
	@docker build -t ldp-jupyter:latest -f docker/jupyter/Dockerfile .

build-all: build-airflow build-spark build-jupyter

# Clean local resources
clean-data:
	@echo "Cleaning local data directories..."
	@rm -rf data/raw/* data/processed/* data/staging/*
	@touch data/raw/.gitkeep data/processed/.gitkeep data/staging/.gitkeep

# Development helpers
dev-requirements:
	@pip install -r docker/airflow/requirements.txt
	@pip install -r docker/spark/requirements.txt
	@pip install pytest pytest-cov

format:
	@echo "Formatting Python code..."
	@black airflow/ spark/ tests/ examples/

lint:
	@echo "Linting Python code..."
	@pylint airflow/ spark/ tests/ examples/ || true
	@flake8 airflow/ spark/ tests/ examples/ || true

# Load example code for demo/testing
load-examples:
	@echo "Loading example code into project directories..."
	@echo "This will copy example DAGs, Spark jobs, and libraries."
	@echo ""
	@echo "Copying DAGs to airflow/dags/..."
	@cp -r examples/dags/* airflow/dags/ 2>/dev/null || true
	@echo "Copying Spark jobs to spark/jobs/..."
	@cp -r examples/spark-jobs/* spark/jobs/ 2>/dev/null || true
	@echo "Copying Spark libraries to spark/lib/..."
	@cp -r examples/spark-lib/* spark/lib/ 2>/dev/null || true
	@echo ""
	@echo "✓ Example code loaded successfully!"
	@echo "You can now test the platform with example pipelines."
	@echo ""
	@echo "Next steps:"
	@echo "  1. Restart platform: make stop && make start"
	@echo "  2. Access Airflow UI and trigger example DAGs"
	@echo "  3. Check logs: make logs"
