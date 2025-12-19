# LDP Dependency Upgrade Plan - 2025

## Current Status

As of December 2025, the project is using older versions of dependencies. This document outlines a phased approach to upgrading them.

⚠️ **IMPORTANT**: The initial attempt to upgrade everything at once caused compatibility issues. This document provides a safer, incremental approach.

---

## Summary of Available Updates

### Terraform Providers

| Component | Current | Latest | Risk Level | Notes |
|-----------|---------|--------|------------|-------|
| Kubernetes Provider | ~> 2.23 | 3.0.1 | 🔴 HIGH | Breaking changes - requires code migration |
| Helm Provider | ~> 2.11 | 3.1.1 | 🔴 HIGH | Breaking changes - requires code migration |

### Helm Charts

| Component | Current | Latest | Risk Level | Notes |
|-----------|---------|--------|------------|-------|
| Airflow | 1.18.0 | 1.18.0 | ✅ NONE | Already up to date |
| MinIO | 5.0.14 | 5.4.0 | 🟡 MEDIUM | Minor version bump |

### Python Packages

| Package | Current | Latest | Risk Level | Component(s) | Notes |
|---------|---------|--------|------------|--------------|-------|
| **Core Processing** |
| pandas | 2.1.4 | 2.3.3 | 🟢 LOW | All | Minor version update |
| numpy | 1.26.3 | 2.3.5 | 🟠 MEDIUM-HIGH | All | **Major version** - may have breaking changes |
| pyarrow | 14.0.2 | 22.0.0 | 🔴 HIGH | All | **Major version** - significant jump |
| **Spark** |
| pyspark | 3.5.0 | 4.0.1 | 🔴 HIGH | Spark, Jupyter | Requires Python >= 3.10, Iceberg 4.0 only |
| pyiceberg | 0.6.1 | 0.10.0 | 🟡 MEDIUM | Spark | Significant version jump |
| **Jupyter** |
| jupyterlab | 4.0.11 | 4.5.1 | 🟢 LOW | Jupyter | Safe minor version update |

---

## Critical Compatibility Issues Discovered

### 1. PySpark and Iceberg Compatibility
- **PySpark 4.1.0** (latest) is NOT compatible with Apache Iceberg
- Apache Iceberg only supports up to **Spark 4.0** (not 4.1)
- **Recommendation**: Use PySpark 4.0.1 instead of 4.1.0

### 2. Terraform Provider v3 Migration
- Requires changing ALL Kubernetes resources from `kubernetes_*` to `kubernetes_*_v1`
- Requires changing Helm provider `kubernetes` block syntax
- This is a **large code change** affecting multiple files

### 3. NumPy 2.x Breaking Changes
- NumPy 2.x has breaking changes from 1.x
- May affect pandas, pyarrow, and other scientific packages
- Needs careful testing

---

## Recommended Phased Approach

### Phase 1: Low-Risk Python Updates ✅ COMPLETED

**Goal**: Update packages with minimal breaking changes

**Updates**:
```yaml
# docker/airflow/requirements.txt
pandas: 2.1.4 → 2.3.3 ✅

# docker/jupyter/requirements.txt
jupyterlab: 4.0.11 → 4.5.1 ✅
pandas: 2.1.4 → 2.3.3 ✅
```

**Status**: ✅ **COMPLETED** on 2025-12-19
- Branch: `phase1-low-risk-python-updates`
- Updated pandas to 2.3.3 in both Airflow and Jupyter
- Updated jupyterlab to 4.5.1

**Next Steps**:
1. Rebuild Docker images: `make build`
2. Test locally: `make start`
3. Verify Airflow DAGs load
4. Test Jupyter notebooks
5. Run example pipelines
6. If successful, merge and move to Phase 2

**Rollback**: Easy - just revert the requirements files

---

### Phase 2: MinIO Helm Chart ✅ COMPLETED

**Goal**: Update MinIO chart for bug fixes and improvements

**Updates**:
```hcl
# terraform/modules/minio/main.tf
version = "5.0.14" → "5.4.0" ✅
```

**Status**: ✅ **COMPLETED** on 2025-12-19
- Branch: `phase2-minio-helm-chart-update`
- Updated MinIO Helm chart from 5.0.14 to 5.4.0

**Next Steps**:
1. Run `terraform init -upgrade` to update provider plugins
2. Run `terraform plan -var-file=environments/local.tfvars` to see changes
3. Run `terraform apply -var-file=environments/local.tfvars` to apply
4. Verify MinIO console and API work
5. Test S3 operations:
   ```bash
   mc alias set ldp http://minio:9000 admin minioadmin
   mc ls ldp/
   ```

**Rollback**: Revert Terraform change and re-apply

---

### Phase 3: PyIceberg Update ✅ COMPLETED

**Goal**: Update PyIceberg for better Iceberg support

**Updates**:
```yaml
# docker/spark/requirements.txt
pyiceberg[s3fs]: 0.6.1 → 0.10.0 ✅
```

**Status**: ✅ **COMPLETED** on 2025-12-19
- Branch: `phase3-pyiceberg-update`
- Updated PyIceberg from 0.6.1 to 0.10.0
- Keeping PySpark at 3.5.0 (Phase 5 will upgrade to 4.0.1)

**Next Steps - Testing Required**:
1. Rebuild Docker images: `make build`
2. Deploy locally: `make start`
3. Test Iceberg table operations:
   - Create Iceberg tables
   - Read/write operations
   - Table maintenance operations
   - Verify metadata compatibility
4. Verify S3/MinIO integration

**Known Issues to Watch For**:
- May require fsspec version adjustments
- Test with existing Iceberg tables
- Monitor for dependency conflicts

---

### Phase 4: Terraform Provider Migration ✅ COMPLETED

**Goal**: Migrate to Terraform Kubernetes Provider v3 and Helm Provider v3

**Status**: ✅ **COMPLETED** on 2025-12-19
- Branch: `phase4-terraform-provider-v3-migration`
- Updated Kubernetes provider from v2.23 to v3.0
- Updated Helm provider from v2.11 to v3.1
- Migrated all Kubernetes resources to _v1 variants
- Updated all resource references across 7 terraform files
- Terraform validation passed successfully

**Files Modified**:
- `terraform/versions.tf` - Updated provider versions and Helm provider syntax
- `terraform/main.tf` - Updated resources and references
- `terraform/outputs.tf` - Updated resource references
- `terraform/modules/monitoring/main.tf` - Updated resources
- `terraform/modules/monitoring/outputs.tf` - Updated references
- `terraform/modules/postgresql/main.tf` - Updated resources
- `terraform/modules/spark/main.tf` - Updated resources

**Next Steps - CRITICAL TESTING REQUIRED**:
⚠️ This is a major infrastructure change. Test thoroughly before using in production!

1. Run `terraform init -upgrade` to download new provider versions
2. Run `terraform plan -var-file=environments/local.tfvars` and review ALL changes
3. Deploy to a test environment first (NOT production)
4. Verify all services start correctly:
   - All pods are running
   - Services are accessible
   - Helm releases are healthy
5. Test complete platform functionality
6. If successful, carefully apply to other environments

**Rollback**:
- Revert the branch and re-apply with old providers
- May require `terraform state` manipulation if already applied

---

**Original Migration Details** (for reference):

**Code Changes Completed**:

1. **Update provider versions** (`terraform/versions.tf`):
```hcl
# Before
terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }
}

provider "helm" {
  kubernetes {
    config_path    = "~/.kube/config"
    config_context = "minikube"
  }
}

# After
terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 3.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 3.1"
    }
  }
}

provider "helm" {
  kubernetes = {  # Changed from block to attribute
    config_path    = "~/.kube/config"
    config_context = "minikube"
  }
}
```

2. **Update ALL Kubernetes resources to v1 versions**:

Files to modify:
- `terraform/main.tf`
- `terraform/outputs.tf`
- `terraform/modules/monitoring/main.tf`
- `terraform/modules/monitoring/outputs.tf`
- `terraform/modules/postgresql/main.tf`
- `terraform/modules/spark/main.tf`

Resource mappings:
```hcl
# Resource declarations
kubernetes_namespace        → kubernetes_namespace_v1
kubernetes_secret          → kubernetes_secret_v1
kubernetes_deployment      → kubernetes_deployment_v1
kubernetes_service         → kubernetes_service_v1
kubernetes_config_map      → kubernetes_config_map_v1
kubernetes_stateful_set    → kubernetes_stateful_set_v1

# Resource references (in other resources and outputs)
kubernetes_namespace.ldp                    → kubernetes_namespace_v1.ldp
kubernetes_secret.platform_secrets          → kubernetes_secret_v1.platform_secrets
kubernetes_config_map.prometheus_config     → kubernetes_config_map_v1.prometheus_config
# ... and all other references
```

**Migration Script** (USE WITH CAUTION):
```bash
#!/bin/bash
# Navigate to terraform directory
cd terraform

# Backup current state
git checkout -b terraform-v3-migration

# Update resource declarations
find . -name "*.tf" -type f -exec sed -i 's/resource "kubernetes_namespace"/resource "kubernetes_namespace_v1"/g' {} +
find . -name "*.tf" -type f -exec sed -i 's/resource "kubernetes_secret"/resource "kubernetes_secret_v1"/g' {} +
find . -name "*.tf" -type f -exec sed -i 's/resource "kubernetes_deployment"/resource "kubernetes_deployment_v1"/g' {} +
find . -name "*.tf" -type f -exec sed -i 's/resource "kubernetes_service"/resource "kubernetes_service_v1"/g' {} +
find . -name "*.tf" -type f -exec sed -i 's/resource "kubernetes_config_map"/resource "kubernetes_config_map_v1"/g' {} +
find . -name "*.tf" -type f -exec sed -i 's/resource "kubernetes_stateful_set"/resource "kubernetes_stateful_set_v1"/g' {} +

# Update resource references
find . -name "*.tf" -type f -exec sed -i 's/kubernetes_namespace\./kubernetes_namespace_v1./g' {} +
find . -name "*.tf" -type f -exec sed -i 's/kubernetes_secret\./kubernetes_secret_v1./g' {} +
find . -name "*.tf" -type f -exec sed -i 's/kubernetes_deployment\./kubernetes_deployment_v1./g' {} +
find . -name "*.tf" -type f -exec sed -i 's/kubernetes_service\./kubernetes_service_v1./g' {} +
find . -name "*.tf" -type f -exec sed -i 's/kubernetes_config_map\./kubernetes_config_map_v1./g' {} +
find . -name "*.tf" -type f -exec sed -i 's/kubernetes_stateful_set\./kubernetes_stateful_set_v1./g' {} +

# Validate
terraform init -backend=false -upgrade
terraform validate
```

**Testing Plan**:
1. Create a separate branch for this migration
2. Run the migration script
3. `terraform validate` - must pass
4. `terraform plan` - review ALL changes carefully
5. Deploy to a test environment (NOT production)
6. Verify all services come up correctly
7. Test complete platform functionality

**Rollback**:
- Delete the migration branch
- Use `terraform state` commands if already applied
- May need to manually fix state

**Time Estimate**: 2-4 hours for migration + testing

---

### Phase 5: PySpark 4.0 Migration ✅ COMPLETED

**Goal**: Upgrade to PySpark 4.0 for performance improvements

**Status**: ✅ **COMPLETED** on 2025-12-19
- Branch: `phase5-pyspark-4.0-migration`
- Updated PySpark from 3.5.0 to 4.0.1
- Updated Spark Docker base image to 4.0.1-python3
- Updated Iceberg runtime JAR: Spark 3.5/Scala 2.12 → Spark 4.0/Scala 2.13
- Updated Hadoop AWS from 3.3.4 to 3.4.1

**Files Modified**:
- `docker/spark/requirements.txt` - PySpark 3.5.0 → 4.0.1
- `docker/jupyter/requirements.txt` - PySpark 3.5.0 → 4.0.1
- `docker/spark/Dockerfile` - Spark base image 3.5.0 → 4.0.1
- `docker/jupyter/Dockerfile` - Updated Spark packages for 4.0

**Breaking Changes Applied**:
- Python >= 3.10 required (provided by base images)
- Scala version changed: 2.12 → 2.13
- Iceberg runtime JAR updated for Spark 4.0
- Hadoop AWS library updated: 3.3.4 → 3.4.1

**Next Steps - CRITICAL TESTING REQUIRED**:
⚠️ This is a major Spark upgrade. Test thoroughly!

1. Rebuild Docker images: `make build`
2. Deploy locally: `make start`
3. Testing checklist:
   - [ ] Spark master/worker start correctly
   - [ ] Spark UI accessible
   - [ ] Submit test Spark job
   - [ ] Read/write to MinIO
   - [ ] Iceberg table operations
   - [ ] Jupyter can connect to Spark
   - [ ] Run existing Airflow + Spark DAGs
   - [ ] Check for any PySpark 4.0 API deprecation warnings
   - [ ] Performance benchmarks

**Rollback**:
- Revert Docker image changes
- Rebuild images with `make build`
- Redeploy with `make start`

---

### Phase 6: NumPy 2.x + PyArrow Major Update ✅ COMPLETED

**Goal**: Update to latest NumPy and PyArrow

**Status**: ✅ **COMPLETED** on 2025-12-19
- Branch: `phase6-numpy-pyarrow-update`
- Updated NumPy from 1.26.3 to 2.3.5 (Major version)
- Updated PyArrow from 14.0.2 to 22.0.0 (Major version)
- Updated pandas in Spark requirements from 2.1.4 to 2.3.3

**Updates Applied**:
```yaml
# All requirements.txt files
numpy: 1.26.3 → 2.3.5 ✅
pyarrow: 14.0.2 → 22.0.0 ✅
pandas (Spark): 2.1.4 → 2.3.3 ✅
```

**Files Modified**:
- `docker/spark/requirements.txt`
- `docker/jupyter/requirements.txt`
- `docker/airflow/requirements.txt`

**Breaking Changes to Monitor**:
- NumPy 2.x dtype system changes
- NumPy 2.x removed deprecated APIs
- PyArrow 22.x schema compatibility changes
- pandas/NumPy 2.x integration
- PySpark/PyArrow 22.x compatibility
- Iceberg/PyArrow 22.x compatibility

**Next Steps - CRITICAL TESTING REQUIRED**:
⚠️ This is the HIGHEST RISK upgrade. Extensive testing is mandatory!

1. Rebuild Docker images: `make build`
2. Deploy locally: `make start`
3. Testing checklist:
   - [ ] All Docker images build successfully
   - [ ] NumPy array operations work correctly
   - [ ] PyArrow table read/write operations
   - [ ] pandas DataFrame operations
   - [ ] PySpark DataFrame operations
   - [ ] Data type conversions between libraries
   - [ ] Spark jobs execute successfully
   - [ ] Iceberg table operations (create, read, write)
   - [ ] S3/MinIO data operations
   - [ ] Airflow DAGs run without errors
   - [ ] Jupyter notebooks execute correctly
   - [ ] Existing data pipelines work end-to-end
   - [ ] Data integrity validation
   - [ ] Check for deprecation warnings
   - [ ] Performance benchmarks

**Known Risks**:
- NumPy 2.x has breaking changes - monitor dtype handling
- PyArrow 22.x is a major version jump (8 versions forward)
- Integration issues between pandas, NumPy 2.x, and PyArrow 22.x
- Potential serialization/deserialization changes

**Rollback**:
- Revert the branch changes
- Rebuild Docker images with `make build`
- Redeploy with `make start`

---

## Alternative: Conservative Approach

If you want to minimize risk, here's what you can safely update NOW:

### Safe Updates Only

```yaml
# Airflow
pandas==2.3.3  # from 2.1.4

# Jupyter
jupyterlab==4.5.1  # from 4.0.11
pandas==2.3.3  # from 2.1.4

# MinIO Helm Chart
version = "5.4.0"  # from 5.0.14
```

**Skip these updates for now**:
- ❌ Terraform providers (too much code change)
- ❌ PySpark 4.0 (significant migration effort)
- ❌ NumPy 2.x (breaking changes)
- ❌ PyArrow 22.x (major version jump)
- ❌ PyIceberg (wait for PySpark 4.0)

**Benefits**:
- Low risk
- Minimal testing required
- Easy rollback
- Still get improvements

---

## Decision Matrix

Use this to decide which updates to pursue:

| Update | Benefit | Risk | Effort | Status |
|--------|---------|------|--------|----------|
| pandas 2.3.3 | Bug fixes, minor features | 🟢 Low | 🟢 Low | ✅ COMPLETED |
| jupyterlab 4.5.1 | UI improvements | 🟢 Low | 🟢 Low | ✅ COMPLETED |
| MinIO 5.4.0 | Bug fixes | 🟡 Medium | 🟢 Low | ✅ COMPLETED |
| PyIceberg 0.10.0 | Better Iceberg support | 🟡 Medium | 🟡 Medium | ✅ COMPLETED |
| Terraform v3 | Future compatibility | 🔴 High | 🔴 High | ✅ COMPLETED |
| PySpark 4.0 | Performance, features | 🔴 High | 🔴 High | ✅ COMPLETED |
| NumPy 2.x | Future compatibility | 🔴 High | 🟠 Medium | ✅ COMPLETED |
| PyArrow 22.x | Performance, features | 🔴 High | 🟠 Medium | ✅ COMPLETED |

---

## Rollback Procedures

### For Python Package Updates
```bash
# 1. Revert changes
git checkout main docker/*/requirements.txt

# 2. Rebuild images
make build

# 3. Redeploy
make start
```

### For Terraform Changes
```bash
# 1. Revert changes
git checkout main terraform/

# 2. Reinitialize
cd terraform
terraform init -upgrade

# 3. Apply old configuration
terraform apply -var-file=environments/local.tfvars
```

### For Helm Chart Updates
```bash
# Find the release
helm list -n ldp

# Rollback to previous revision
helm rollback <release-name> -n ldp
```

---

## Next Steps

1. **Review this document carefully**
2. **Decide which phases to pursue** based on your needs and risk tolerance
3. **When ready**, ask me to help with specific phases
4. **Test each phase thoroughly** before moving to the next

## Questions to Consider

Before proceeding, ask yourself:

1. **What problems am I trying to solve?** (Performance? Security? Compatibility?)
2. **What's my timeline?** (Immediate need vs. future planning)
3. **What's my risk tolerance?** (Production system vs. development)
4. **Do I have time for proper testing?** (Each phase needs validation)
5. **What happens if something breaks?** (Do I have rollback procedures ready?)

---

## References

- [Terraform Helm Provider v3 Upgrade Guide](https://registry.terraform.io/providers/hashicorp/helm/latest/docs/guides/v3-upgrade-guide)
- [Terraform Kubernetes Provider v3 Upgrade Guide](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs/guides/v3-upgrade-guide)
- [PySpark 4.0 Release Notes](https://spark.apache.org/releases/spark-release-4-0-0.html)
- [Apache Iceberg Releases](https://iceberg.apache.org/releases/)
- [NumPy 2.0 Migration Guide](https://numpy.org/devdocs/numpy_2_0_migration_guide.html)

---

**Document Version**: 1.6
**Last Updated**: 2025-12-19
**Status**: All Phases (1-6) Completed - Critical Testing Required for Phase 6 (NumPy 2.x + PyArrow 22.x)
