# Local Data Platform (LDP)

[![CI Testing](https://github.com/gridatek/ldp/actions/workflows/ci.yml/badge.svg)](https://github.com/gridatek/ldp/actions/workflows/ci.yml)
[![Platform Tests](https://github.com/gridatek/ldp/actions/workflows/platform-tests.yml/badge.svg)](https://github.com/gridatek/ldp/actions/workflows/platform-tests.yml)

A complete local data engineering platform running on Minikube with Apache Airflow, Apache Spark, MinIO, PostgreSQL, and Apache Iceberg.

**Supported Platforms**: Linux | macOS | Windows

## What is LDP?

**LDP is a local development and testing environment for data engineering workflows.** It brings enterprise-grade data tools to your laptop, allowing you to:

- **Learn** data engineering concepts without cloud costs
- **Develop** and test data pipelines locally before cloud deployment
- **Prototype** new data architectures and workflows
- **Experiment** with modern data tools (Airflow, Spark, Iceberg)
- **Run CI/CD tests** for data pipelines

### Important: Local Development Only

LDP is designed to run **on your local machine** using Minikube. It is **NOT intended for production use** or cloud deployment. For production workloads, consider:
- Managed services (AWS EMR, Google Cloud Dataproc, Azure Synapse)
- Kubernetes clusters on cloud providers (EKS, GKE, AKS)
- Purpose-built data platforms (Databricks, Snowflake)

LDP gives you a realistic local environment to develop and test before deploying to these production platforms.

## Why Use LDP?

### Perfect For

- ✅ **Data Engineering Students** - Learn industry-standard tools without AWS/GCP bills
- ✅ **Pipeline Development** - Build and debug Airflow DAGs locally before cloud deployment
- ✅ **Testing & CI/CD** - Run integration tests for data pipelines in GitHub Actions
- ✅ **Proof of Concepts** - Validate data architecture decisions quickly
- ✅ **Tool Evaluation** - Try Iceberg, Spark, or Airflow features risk-free

### Not Suitable For

- ❌ Production data workloads (use cloud services instead)
- ❌ Large-scale data processing (limited by laptop resources)
- ❌ Multi-user production environments
- ❌ Long-running production jobs
- ❌ Enterprise SLA requirements

## Features

- **Apache Airflow** - Workflow orchestration and scheduling
- **Apache Spark** - Distributed data processing (batch and streaming)
- **MinIO** - S3-compatible object storage
- **PostgreSQL** - Metadata store for Airflow and Hive
- **Apache Iceberg** - Modern table format with ACID transactions
- **Jupyter** - Interactive development environment

## Quick Start

LDP works on **macOS**, **Windows**, and **Linux**. Choose your platform:

- **[macOS](docs/platform-guides/macos.md)** - Use Homebrew and native tools
- **[Windows](docs/platform-guides/windows.md)** - Use PowerShell scripts and Chocolatey/winget
- **[Linux](docs/setup-guide.md#linux-setup)** - Standard package managers

### Prerequisites

Install the required tools:
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Terraform](https://developer.hashicorp.com/terraform/install)
- [Helm](https://helm.sh/docs/intro/install/)

### Setup and Deploy

**Linux/macOS:**
```bash
# 1. Initial setup (starts Minikube)
make setup

# 2. Deploy the platform
make start

# 3. Check service health
make health
```

**Windows PowerShell:**
```powershell
# 1. Initial setup
.\scripts\windows\setup.ps1

# 2. Deploy the platform
.\scripts\windows\start.ps1

# 3. Check service health
.\scripts\windows\check-health.ps1
```

### Access Services

After deployment, get your Minikube IP:
```bash
make minikube-ip
```

Access the services at:

- **Airflow UI**: `http://<minikube-ip>:30080`
  - Username: `admin`
  - Password: `admin`

- **MinIO Console**: `http://<minikube-ip>:30901`
  - Username: `admin`
  - Password: `minioadmin`

- **Spark Master UI**: `http://<minikube-ip>:30707`

- **Jupyter**: `http://<minikube-ip>:30888`
  - Get token: `kubectl logs -n ldp deployment/jupyter`

### Alternative: Port Forwarding

If NodePort access doesn't work, use port forwarding:

```bash
make airflow-forward   # http://localhost:8080
make minio-forward     # http://localhost:9001
make spark-forward     # http://localhost:8080
make jupyter-forward   # http://localhost:8888
```

## Project Structure

```
ldp/
├── terraform/          # Infrastructure as Code
│   ├── modules/        # Terraform modules (airflow, spark, minio, postgresql)
│   ├── environments/   # Environment-specific configs
│   └── helm-values/    # Custom Helm values
├── kubernetes/         # Additional K8s manifests
├── airflow/            # Airflow DAGs and plugins
├── spark/              # Spark jobs and libraries
├── docker/             # Custom Docker images
├── scripts/            # Utility scripts
├── data/               # Local data storage
├── config/             # Configuration files
├── tests/              # Integration and E2E tests
└── examples/           # Example code
```

## Testing

LDP is tested across multiple platforms using GitHub Actions:
- **Windows** - PowerShell scripts, Terraform, Python
- **macOS** - Bash scripts, Terraform, Python
- **Linux** - Full E2E tests with Minikube

See [CI/CD Testing Documentation](docs/ci-testing.md) for details.

## Common Operations

### Managing the Platform

```bash
# Start the platform
make start

# Stop the platform
make stop

# Complete cleanup
make cleanup

# Check health
make health

# View pods
make pods

# View services
make services
```

### Initialize MinIO Buckets

```bash
make init-minio
```

### Running Tests

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests
make test-int
```

## Getting Started with Your Code

### Start with a Clean Slate

LDP provides an **empty project structure** - a blank canvas for your data pipelines. The main directories (`airflow/dags/`, `spark/jobs/`, `spark/lib/`) are intentionally empty, giving you complete freedom to build your own solutions.

### Option 1: Load Examples (Recommended for Learning)

Want to see working examples first? Load the example code:

```bash
make load-examples
```

This copies example DAGs, Spark jobs, and libraries into your project directories. Great for:
- Learning how to structure your code
- Understanding integration patterns
- Quick demos and testing
- Starting point for customization

### Option 2: Start from Scratch

Ready to build your own? Just create files in the right places:

```bash
# Create your first DAG
vim airflow/dags/my_pipeline.py

# Create your first Spark job
vim spark/jobs/process_data.py
```

**Where to write your code:**
- `airflow/dags/` - Your workflow orchestration (DAGs)
- `spark/jobs/` - Your data processing logic
- `spark/lib/` - Reusable utilities and functions
- `data/raw/` - Your input datasets

📖 **See [Writing Code Guide](docs/writing-code.md) for detailed instructions and best practices**

## Development Workflow

### 1. Write Your Code

```python
# airflow/dags/my_etl.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

with DAG('my_etl', start_date=datetime(2024, 1, 1)) as dag:
    task = PythonOperator(
        task_id='process',
        python_callable=lambda: print("Processing data!")
    )
```

### 2. Add Your Data

```bash
cp ~/my_dataset.csv data/raw/
```

### 3. Deploy and Test

```bash
# Restart to load new code
make stop && make start

# Access Airflow UI and trigger your DAG
open http://$(minikube ip):30080
```

### Working with Iceberg

See `examples/iceberg_crud.py` for complete examples:

```python
# Create Iceberg table
spark.sql("""
    CREATE TABLE local.db.my_table (
        id BIGINT,
        data STRING
    ) USING iceberg
""")
```

## Configuration

### Environment Variables

Copy and customize the environment file:

```bash
cp config/env/.env.example .env
```

### Terraform Variables

Customize deployment in `terraform/environments/`:
- `local.tfvars` - Local development (default)

Apply with local configuration:
```bash
cd terraform
terraform apply -var-file=environments/local.tfvars
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n ldp

# Describe problematic pod
kubectl describe pod <pod-name> -n ldp

# Check logs
kubectl logs <pod-name> -n ldp
```

### Out of Resources

Increase Minikube resources:

```bash
minikube delete
minikube start --cpus=6 --memory=12288 --disk-size=60g
```

### Persistent Volume Issues

```bash
# Check PVCs
kubectl get pvc -n ldp

# Delete and recreate
kubectl delete pvc <pvc-name> -n ldp
make start
```

## Examples

The `examples/` directory contains reference implementations:

```
examples/
├── simple_dag.py           # Basic Airflow DAG
├── spark_job.py            # Simple Spark job
├── iceberg_crud.py         # Iceberg table operations
├── minio_operations.py     # MinIO/S3 operations
├── dags/                   # Complete DAG examples
│   ├── example_spark_job.py
│   ├── data_ingestion/
│   └── data_transformation/
├── spark-jobs/             # Complete Spark job examples
│   ├── batch_processing.py
│   ├── streaming_job.py
│   └── iceberg_maintenance.py
└── spark-lib/              # Reusable library examples
    ├── transformations.py
    ├── data_quality.py
    └── utils.py
```

**Load examples into your project:**
```bash
make load-examples
```

This copies all examples to their respective directories for testing and learning.

## Documentation

See the **[Documentation Index](docs/)** for detailed guides, architecture documentation, and troubleshooting.

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests: `make test`
4. Submit a pull request

## License

MIT License

## Support

For issues and questions, please open an issue in the repository.
