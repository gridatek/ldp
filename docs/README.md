# LDP Documentation

Welcome to the Local Data Platform (LDP) documentation.

## Getting Started

- **[Setup Guide](setup-guide.md)** - Step-by-step installation and deployment instructions
  - Prerequisites and software requirements
  - Minikube setup and configuration
  - Terraform deployment
  - Service access and verification
  - Iceberg configuration examples

## Architecture & Design

- **[Project Structure](project-structure.md)** - Complete directory structure and organization
  - Terraform modules layout
  - Airflow DAGs and plugins structure
  - Spark jobs and libraries
  - Docker images and configurations
  - Testing structure

## Operations

- **[Production-Ready Local Deployment](production-guide.md)** - Best practices for local environments
  - Security configuration (secrets, RBAC, network policies)
  - Monitoring setup (Prometheus, Grafana)
  - Performance tuning
  - Backup and recovery
  - Troubleshooting common issues
  - Operational runbook

- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions
  - Pod startup problems
  - Resource constraints
  - Networking issues
  - Database connection problems

## Quick Reference

### What is LDP?

LDP is a **local development environment** that brings enterprise data engineering tools to your laptop:
- Learn data engineering without cloud costs
- Develop and test pipelines locally
- Prototype data architectures
- Run CI/CD tests for data workflows

### Not For Production

LDP is designed for local development only. For production workloads, use cloud-managed services (AWS EMR/Glue, GCP Dataproc/Composer, Azure Synapse, or platforms like Databricks/Snowflake).

### Technology Stack

- **Apache Airflow** - Workflow orchestration
- **Apache Spark** - Distributed data processing
- **Apache Iceberg** - Modern table format
- **MinIO** - S3-compatible object storage
- **PostgreSQL** - Metadata store
- **Jupyter** - Interactive development

## Contributing

To contribute to the documentation:
1. Create a branch for your changes
2. Update the relevant documentation files
3. Update this index if adding new docs
4. Submit a pull request

## Need Help?

- Check the [Troubleshooting Guide](troubleshooting.md)
- Review the [Setup Guide](setup-guide.md) for common setup issues
- Open an issue in the repository
