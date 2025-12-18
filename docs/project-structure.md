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
│   ├── dags/
│   │   ├── __init__.py
│   │   ├── example_spark_job.py
│   │   ├── data_ingestion/
│   │   │   ├── __init__.py
│   │   │   └── ingest_daily.py
│   │   └── data_transformation/
│   │       ├── __init__.py
│   │       └── transform_pipeline.py
│   │
│   ├── plugins/
│   │   ├── __init__.py
│   │   └── custom_operators/
│   │       ├── __init__.py
│   │       └── iceberg_operator.py
│   │
│   ├── config/
│   │   ├── airflow.cfg
│   │   └── webserver_config.py
│   │
│   └── tests/
│       ├── __init__.py
│       └── test_dags.py
│
├── spark/                        # Spark applications
│   ├── jobs/
│   │   ├── __init__.py
│   │   ├── batch_processing.py
│   │   ├── streaming_job.py
│   │   └── iceberg_maintenance.py
│   │
│   ├── lib/
│   │   ├── __init__.py
│   │   ├── utils.py
│   │   ├── transformations.py
│   │   └── io_helpers.py
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
│   └── tests/
│       ├── __init__.py
│       └── test_transformations.py
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
│   ├── hive/
│   │   └── hive-site.xml
│   └── env/
│       ├── .env.example
│       └── dev.env
│
├── docs/                         # Documentation
│   ├── setup.md
│   ├── architecture.md
│   ├── troubleshooting.md
│   ├── development.md
│   └── images/
│       └── architecture-diagram.png
│
├── tests/                        # Integration tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── integration/
│   │   ├── test_airflow_spark.py
│   │   ├── test_minio_access.py
│   │   └── test_iceberg_tables.py
│   └── e2e/
│       └── test_pipeline.py
│
├── monitoring/                   # Monitoring configs (optional)
│   ├── prometheus/
│   │   └── prometheus.yml
│   └── grafana/
│       └── dashboards/
│
└── examples/                     # Example code and demos
    ├── simple_dag.py
    ├── spark_job.py
    ├── iceberg_crud.py
    └── minio_operations.py
```

## Directory Descriptions

### `/terraform`
Infrastructure as Code for deploying all platform components to Kubernetes. Modularized for reusability and maintainability.

### `/kubernetes`
Additional Kubernetes manifests not managed by Helm, such as ConfigMaps, Jobs, and custom resources.

### `/airflow`
All Airflow-related code including DAGs, plugins, and custom operators. Mounted into Airflow pods.

### `/spark`
Spark applications, libraries, notebooks, and SQL scripts. Contains both batch and streaming job definitions.

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
Unit, integration, and end-to-end tests for validating the platform.

### `/monitoring`
Observability configurations for Prometheus and Grafana (optional enhancement).

### `/examples`
Sample code demonstrating platform capabilities.

## Key Files

- **Makefile**: Automates common tasks
- **README.md**: Quick start and overview
- **.env.example**: Template for environment variables
- **requirements.txt**: Python dependencies

## Usage Patterns

### Development Workflow
1. Modify code in `/airflow/dags` or `/spark/jobs`
2. Test locally using `/scripts/start.sh`
3. Access services via Minikube NodePorts
4. Check logs and debug
5. Commit changes (excluding generated files)

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