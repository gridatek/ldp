# Local Data Platform - Project Structure

```
ldp/
├── README.md                      # Project overview and quick start
├── .gitignore                     # Git ignore rules
├── Makefile                       # Common commands automation
│
├── terraform/                     # Infrastructure as Code
│   ├── main.tf                   # Main Terraform configuration
│   ├── variables.tf              # Input variables
│   ├── outputs.tf                # Output values
│   ├── versions.tf               # Provider versions
│   ├── locals.tf                 # Local values
│   │
│   ├── modules/                  # Reusable Terraform modules
│   │   ├── airflow/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── spark/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── minio/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   └── postgresql/
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       └── outputs.tf
│   │
│   ├── environments/             # Environment-specific configs
│   │   └── local.tfvars          # Local development configuration
│   │
│   └── helm-values/              # Custom Helm values
│       ├── airflow-values.yaml
│       ├── spark-values.yaml
│       ├── minio-values.yaml
│       └── postgresql-values.yaml
│
├── kubernetes/                    # Additional K8s manifests
│   ├── namespace.yaml
│   ├── configmaps/
│   │   ├── spark-config.yaml
│   │   └── airflow-config.yaml
│   ├── secrets/
│   │   └── .gitkeep             # Secrets should not be committed
│   └── jobs/
│       └── init-minio-buckets.yaml
│
├── airflow/                      # Airflow DAGs and configs
│   ├── dags/                     # Your DAGs go here (empty by default)
│   │   └── __init__.py
│   │
│   ├── plugins/                  # Generic reusable plugins
│   │   ├── __init__.py
│   │   └── custom_operators/
│   │       ├── __init__.py
│   │       └── iceberg_operator.py  # Generic Iceberg operator
│   │
│   ├── config/
│   │   ├── airflow.cfg
│   │   └── webserver_config.py
│   │
│   └── tests/                    # Your tests go here (empty by default)
│       └── __init__.py
│
├── spark/                        # Spark applications
│   ├── jobs/                     # Your Spark jobs go here (empty by default)
│   │   └── __init__.py
│   │
│   ├── lib/                      # Your Spark libraries go here (empty by default)
│   │   └── __init__.py
│   │
│   ├── config/
│   │   ├── spark-defaults.conf
│   │   └── log4j.properties
│   │
│   ├── notebooks/                # Jupyter notebooks
│   │   ├── exploratory_analysis.ipynb
│   │   ├── iceberg_demo.ipynb
│   │   └── spark_optimization.ipynb
│   │
│   ├── sql/                      # SQL scripts
│   │   ├── create_tables.sql
│   │   └── queries/
│   │       └── analytics.sql
│   │
│   └── tests/                    # Your tests go here (empty by default)
│       └── __init__.py
│
├── docker/                       # Custom Docker images
│   ├── airflow/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── spark/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── jars/
│   │       └── .gitkeep
│   │
│   └── jupyter/
│       ├── Dockerfile
│       └── requirements.txt
│
├── scripts/                      # Utility scripts
│   ├── setup.sh                 # Initial setup script
│   ├── start.sh                 # Start Minikube and deploy
│   ├── stop.sh                  # Stop services
│   ├── cleanup.sh               # Cleanup resources
│   ├── port-forward.sh          # Port forwarding helper
│   ├── init-minio.sh            # Initialize MinIO buckets
│   └── check-health.sh          # Health check script
│
├── data/                         # Local data directory
│   ├── raw/
│   │   └── .gitkeep
│   ├── processed/
│   │   └── .gitkeep
│   ├── staging/
│   │   └── .gitkeep
│   └── sample/                  # Sample datasets
│       └── sample_data.csv
│
├── config/                       # Application configs
│   ├── iceberg/
│   │   └── catalog.properties
│   └── hive/
│       └── hive-site.xml
│
├── docs/                         # Documentation
│   ├── setup.md
│   ├── architecture.md
│   ├── troubleshooting.md
│   ├── development.md
│   └── images/
│       └── architecture-diagram.png
│
├── tests/                        # Your integration tests (empty by default)
│   ├── __init__.py
│   ├── integration/
│   │   └── __init__.py
│   └── e2e/
│       └── __init__.py
│
├── monitoring/                   # Monitoring configs (optional)
│   ├── prometheus/
│   │   └── prometheus.yml
│   └── grafana/
│       └── dashboards/
│
└── examples/                     # Example code and demos
    ├── simple_dag.py             # Standalone example files
    ├── spark_job.py
    ├── iceberg_crud.py
    ├── minio_operations.py
    │
    ├── dags/                     # Example Airflow DAGs
    │   ├── example_spark_job.py
    │   ├── data_ingestion/
    │   │   ├── __init__.py
    │   │   └── ingest_daily.py
    │   └── data_transformation/
    │       ├── __init__.py
    │       └── transform_pipeline.py
    │
    ├── spark-jobs/               # Example Spark jobs
    │   ├── batch_processing.py
    │   ├── streaming_job.py
    │   └── iceberg_maintenance.py
    │
    ├── spark-lib/                # Example Spark libraries
    │   ├── utils.py
    │   ├── transformations.py
    │   ├── data_quality.py
    │   ├── io_helpers.py
    │   └── metrics.py
    │
    └── tests/                    # Example tests
        ├── __init__.py
        ├── conftest.py
        ├── airflow/
        │   ├── __init__.py
        │   └── test_dags.py
        ├── spark/
        │   ├── __init__.py
        │   ├── test_transformations.py
        │   └── test_data_quality.py
        ├── integration/
        │   ├── test_airflow_spark.py
        │   ├── test_minio_access.py
        │   └── test_iceberg_tables.py
        └── e2e/
            └── test_pipeline.py
```

## Directory Descriptions

### `/terraform`
Infrastructure as Code for deploying all platform components to Kubernetes. Modularized for reusability and maintainability.

### `/kubernetes`
Additional Kubernetes manifests not managed by Helm, such as ConfigMaps, Jobs, and custom resources.

### `/airflow`
All Airflow-related code including DAGs, plugins, and custom operators. Mounted into Airflow pods.
- **`dags/`**: Empty by default - add your own DAGs here or use `make load-examples`
- **`plugins/`**: Generic reusable operators (like IcebergTableOperator) that are part of the platform
- **`tests/`**: Empty by default - add your own tests here or use `make load-examples`

### `/spark`
Spark applications, libraries, notebooks, and SQL scripts. Contains both batch and streaming job definitions.
- **`jobs/`**: Empty by default - add your own Spark jobs here or use `make load-examples`
- **`lib/`**: Empty by default - add your own libraries here or use `make load-examples`
- **`tests/`**: Empty by default - add your own tests here or use `make load-examples`

### `/docker`
Custom Docker images for Airflow, Spark, and Jupyter with project-specific dependencies.

### `/scripts`
Bash scripts for common operations like setup, deployment, cleanup, and health checks.

### `/data`
Local data storage for development. Excluded from git except for sample data.

### `/config`
Configuration files for various components (Iceberg, Hive, environment variables).

### `/docs`
Project documentation including setup guides, architecture diagrams, and troubleshooting.

### `/tests`
Integration and end-to-end tests for validating the platform.
- Empty by default - add your own tests here or use `make load-examples` to copy example tests

### `/monitoring`
Observability configurations for Prometheus and Grafana (optional enhancement).

### `/examples`
Complete example code demonstrating platform capabilities including:
- **Standalone scripts**: Simple examples for quick reference
- **`dags/`**: Example Airflow DAGs showing various patterns
- **`spark-jobs/`**: Example Spark batch and streaming jobs
- **`spark-lib/`**: Example reusable Spark libraries and utilities
- **`tests/`**: Complete test suite for all example code

Use `make load-examples` to copy all example code and tests into your project directories for experimentation.

## Key Files

- **Makefile**: Automates common tasks
- **README.md**: Quick start and overview
- **terraform/environments/*.tfvars**: Infrastructure configuration
- **terraform/helm-values/*.yaml**: Kubernetes deployment configuration

## Usage Patterns

### Getting Started
1. **Fresh start**: Project directories are empty by default - add your own code
2. **With examples**: Run `make load-examples` to copy example DAGs, jobs, libraries, and tests
3. **Deploy**: Use `make start` to deploy the platform
4. **Access**: Services available via Minikube NodePorts

### Development Workflow
1. Add your code in `/airflow/dags` or `/spark/jobs`
2. Add corresponding tests in test directories
3. Test locally using `make start`
4. Access services via port forwarding or NodePorts
5. Check logs and debug with `make logs`
6. Commit changes (excluding generated files)

### Adding New Components
1. Create Terraform module in `/terraform/modules`
2. Add configuration in `/config`
3. Update documentation in `/docs`
4. Add examples in `/examples`

### Testing
1. Unit tests in respective component directories
2. Integration tests in `/tests/integration`
3. E2E tests in `/tests/e2e`
4. Run all: `make test`

## Best Practices

- Keep secrets in `.env` files (not committed)
- Use `.gitkeep` for empty directories
- Document all custom configurations
- Version control everything except data/logs
- Use consistent naming conventions
- Modularize Terraform for reusability