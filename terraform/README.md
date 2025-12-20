# Terraform Directory

This directory contains Infrastructure as Code (IaC) for deploying LDP to cloud environments.

## Structure

```
terraform/
├── modules/           # Reusable Terraform modules
├── environments/      # Environment-specific configurations
│   ├── dev/
│   ├── staging/
│   └── prod/
└── README.md          # This file
```

## What is Terraform?

Terraform is an Infrastructure as Code tool that allows you to define and provision infrastructure using a declarative configuration language.

## Purpose

Use Terraform to deploy LDP infrastructure to:

- **AWS** - EKS, S3, RDS, etc.
- **Azure** - AKS, Blob Storage, etc.
- **GCP** - GKE, Cloud Storage, etc.
- **On-premises** - Kubernetes clusters

## Quick Start

### Prerequisites

```bash
# Install Terraform
# macOS
brew install terraform

# Linux
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Verify
terraform version
```

### Initialize

```bash
cd terraform/environments/dev
terraform init
```

### Plan

Preview changes before applying:

```bash
terraform plan
```

### Apply

Deploy infrastructure:

```bash
terraform apply
```

### Destroy

Remove all infrastructure:

```bash
terraform destroy
```

## Directory Structure

### Modules

**Location**: `terraform/modules/`

Reusable infrastructure components:

```
modules/
├── kubernetes/        # Kubernetes cluster (EKS, AKS, GKE)
├── storage/           # Object storage (S3, Blob, GCS)
├── database/          # Managed databases
├── networking/        # VPC, subnets, security groups
└── monitoring/        # CloudWatch, Prometheus, Grafana
```

**Example module usage:**

```hcl
module "kubernetes" {
  source = "../../modules/kubernetes"

  cluster_name    = "ldp-prod"
  cluster_version = "1.28"
  node_count      = 3
  instance_type   = "m5.xlarge"
}
```

### Environments

**Location**: `terraform/environments/`

Environment-specific configurations:

- **dev**: Development environment (small, cost-optimized)
- **staging**: Pre-production environment (production-like)
- **prod**: Production environment (high availability, scaled)

**Example directory structure:**

```
environments/dev/
├── main.tf           # Main configuration
├── variables.tf      # Input variables
├── outputs.tf        # Output values
├── terraform.tfvars  # Variable values
└── backend.tf        # Remote state configuration
```

## Basic Terraform Configuration

### Main Configuration (main.tf)

```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Deploy Kubernetes cluster
module "kubernetes" {
  source = "../../modules/kubernetes"

  cluster_name = "ldp-${var.environment}"
  node_count   = var.node_count
}

# Deploy S3 buckets
module "storage" {
  source = "../../modules/storage"

  bucket_prefix = "ldp-${var.environment}"
  buckets = [
    "datalake",
    "warehouse",
    "archive"
  ]
}
```

### Variables (variables.tf)

```hcl
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "node_count" {
  description = "Number of Kubernetes nodes"
  type        = number
  default     = 3
}
```

### Variable Values (terraform.tfvars)

```hcl
environment = "dev"
aws_region  = "us-east-1"
node_count  = 2
```

### Outputs (outputs.tf)

```hcl
output "cluster_endpoint" {
  description = "Kubernetes cluster endpoint"
  value       = module.kubernetes.endpoint
}

output "bucket_names" {
  description = "Created S3 bucket names"
  value       = module.storage.bucket_names
}
```

## Remote State Management

Use remote state for team collaboration:

**Backend configuration (backend.tf):**

```hcl
terraform {
  backend "s3" {
    bucket = "ldp-terraform-state"
    key    = "dev/terraform.tfstate"
    region = "us-east-1"

    dynamodb_table = "ldp-terraform-locks"
    encrypt        = true
  }
}
```

## Common Resources

### AWS Deployment

```hcl
# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"

  cluster_name    = "ldp-cluster"
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    workers = {
      min_size     = 2
      max_size     = 10
      desired_size = 3

      instance_types = ["m5.large"]
    }
  }
}

# S3 Buckets
resource "aws_s3_bucket" "datalake" {
  bucket = "ldp-datalake-${var.environment}"

  tags = {
    Environment = var.environment
    Project     = "LDP"
  }
}

# RDS for PostgreSQL (Airflow metadata)
resource "aws_db_instance" "postgres" {
  identifier        = "ldp-postgres-${var.environment}"
  engine            = "postgres"
  engine_version    = "16"
  instance_class    = "db.t3.medium"
  allocated_storage = 20

  db_name  = "airflow"
  username = "airflow"
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.database.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  skip_final_snapshot = var.environment != "prod"
}
```

### Kubernetes Deployment

```hcl
# Deploy Airflow
resource "kubernetes_deployment" "airflow" {
  metadata {
    name      = "airflow-webserver"
    namespace = kubernetes_namespace.ldp.metadata[0].name
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "airflow-webserver"
      }
    }

    template {
      metadata {
        labels = {
          app = "airflow-webserver"
        }
      }

      spec {
        container {
          name  = "webserver"
          image = "apache/airflow:3.1.5"

          env {
            name  = "AIRFLOW__CORE__SQL_ALCHEMY_CONN"
            value = var.database_connection_string
          }
        }
      }
    }
  }
}
```

## Best Practices

### 1. Use Modules

Organize reusable infrastructure into modules:

```
modules/
├── storage/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
```

### 2. Separate Environments

Keep environments isolated:

```
environments/
├── dev/
├── staging/
└── prod/
```

### 3. Use Remote State

Store state remotely for collaboration:

```hcl
backend "s3" {
  bucket = "terraform-state"
  key    = "ldp/terraform.tfstate"
}
```

### 4. Tag Resources

Tag all resources for organization and cost tracking:

```hcl
tags = {
  Environment = var.environment
  Project     = "LDP"
  ManagedBy   = "Terraform"
}
```

### 5. Use Variables

Make configurations flexible:

```hcl
variable "instance_type" {
  default = {
    dev     = "t3.medium"
    staging = "m5.large"
    prod    = "m5.xlarge"
  }
}
```

### 6. Validate Before Apply

Always review changes:

```bash
terraform plan -out=tfplan
# Review the plan
terraform apply tfplan
```

### 7. Lock State

Use state locking to prevent concurrent modifications:

```hcl
backend "s3" {
  dynamodb_table = "terraform-locks"
}
```

## Security Best Practices

### 1. Never Commit Secrets

Use AWS Secrets Manager, HashiCorp Vault, or similar:

```hcl
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "ldp/database/password"
}
```

### 2. Use IAM Roles

Don't hardcode AWS credentials:

```hcl
# Use instance profiles or EKS pod identity
```

### 3. Encrypt State

Enable encryption for remote state:

```hcl
backend "s3" {
  encrypt = true
  kms_key_id = "arn:aws:kms:..."
}
```

### 4. Restrict Access

Use least-privilege IAM policies:

```hcl
resource "aws_iam_policy" "terraform" {
  name = "terraform-ldp-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "eks:*",
          "ec2:*",
          "s3:*"
        ]
        Resource = "*"
      }
    ]
  })
}
```

## Workflow

### Initial Setup

```bash
# 1. Configure AWS credentials
aws configure

# 2. Initialize Terraform
cd terraform/environments/dev
terraform init

# 3. Create workspace
terraform workspace new dev

# 4. Plan and apply
terraform plan
terraform apply
```

### Making Changes

```bash
# 1. Edit Terraform files
vim main.tf

# 2. Format code
terraform fmt -recursive

# 3. Validate syntax
terraform validate

# 4. Review changes
terraform plan

# 5. Apply changes
terraform apply
```

### Managing Multiple Environments

```bash
# Switch to staging
terraform workspace select staging

# Or pass var file
terraform apply -var-file=staging.tfvars
```

## Common Commands

```bash
# Initialize
terraform init

# Format code
terraform fmt

# Validate configuration
terraform validate

# Plan changes
terraform plan

# Apply changes
terraform apply

# Destroy infrastructure
terraform destroy

# Show current state
terraform show

# List resources
terraform state list

# Import existing resource
terraform import aws_s3_bucket.example my-bucket
```

## Troubleshooting

### State Lock Issues

```bash
# Force unlock (use carefully!)
terraform force-unlock LOCK_ID
```

### Import Existing Resources

```bash
# Import resource to state
terraform import module.storage.aws_s3_bucket.datalake my-bucket-name
```

### Debug

```bash
# Enable debug logging
export TF_LOG=DEBUG
terraform apply
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Terraform

on:
  push:
    branches: [main]
    paths:
      - 'terraform/**'

jobs:
  terraform:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2

      - name: Terraform Init
        run: terraform init
        working-directory: terraform/environments/prod

      - name: Terraform Plan
        run: terraform plan
        working-directory: terraform/environments/prod

      - name: Terraform Apply
        if: github.ref == 'refs/heads/main'
        run: terraform apply -auto-approve
        working-directory: terraform/environments/prod
```

## Cost Optimization

### Use Auto-scaling

```hcl
eks_managed_node_groups = {
  workers = {
    min_size     = 1
    max_size     = 10
    desired_size = 2
  }
}
```

### Use Spot Instances

```hcl
eks_managed_node_groups = {
  spot = {
    capacity_type = "SPOT"
    instance_types = ["m5.large", "m5a.large"]
  }
}
```

### Tag for Cost Tracking

```hcl
tags = {
  Environment = var.environment
  Project     = "LDP"
  CostCenter  = "DataEngineering"
}
```

## Learn More

- **Terraform Documentation**: https://www.terraform.io/docs
- **AWS Provider**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- **Kubernetes Provider**: https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs
- **Best Practices**: https://www.terraform-best-practices.com/
- **Production Guide**: `docs/production-guide.md`
