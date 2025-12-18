# LDP Documentation

Welcome to the Local Data Platform (LDP) documentation.

## Getting Started

- **[Setup Guide](setup-guide.md)** - Step-by-step installation and deployment instructions
  - Prerequisites and software requirements
  - Minikube setup and configuration
  - Terraform deployment
  - Service access and verification
  - Iceberg configuration examples

- **[Writing Code Guide](writing-code.md)** - Where to write your custom code
  - Directory structure for your code
  - Airflow DAGs, Spark jobs, and libraries
  - Examples and best practices
  - Development workflow
  - Using the `make load-examples` command

### Platform-Specific Guides

LDP supports macOS, Windows, and Linux:

- **[macOS Setup](platform-guides/macos.md)** - Installation guide for Mac (Intel and Apple Silicon)
  - Homebrew installation
  - Docker Desktop setup
  - macOS-specific troubleshooting

- **[Windows Setup](platform-guides/windows.md)** - Installation guide for Windows 10/11
  - Chocolatey/winget installation
  - PowerShell scripts
  - Hyper-V and Docker Desktop options
  - Windows-specific troubleshooting

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

## Testing & CI

- **[CI/CD Testing](ci-testing.md)** - Continuous integration and testing
  - GitHub Actions workflows
  - Platform-specific tests
  - E2E testing on Linux
  - Running tests locally
  - Troubleshooting CI failures

## Contributing

To contribute to the documentation:
1. Create a branch for your changes
2. Update the relevant documentation files
3. Update this index if adding new docs
4. Run tests locally before pushing
5. Submit a pull request

## Need Help?

- Check the [Troubleshooting Guide](troubleshooting.md)
- Review the [Setup Guide](setup-guide.md) for common setup issues
- See [CI/CD Testing](ci-testing.md) for test failures
- Open an issue in the repository
