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

### Phase 2: MinIO Helm Chart (LOW RISK)

**Goal**: Update MinIO chart for bug fixes and improvements

**Updates**:
```hcl
# terraform/modules/minio/main.tf
version = "5.0.14" → "5.4.0"
```

**Steps**:
1. Update version in `terraform/modules/minio/main.tf`
2. Run `terraform plan` to see changes
3. Run `terraform apply` on test environment
4. Verify MinIO console and API work
5. Test S3 operations

**Testing**:
```bash
# Test MinIO connectivity
mc alias set ldp http://minio:9000 admin minioadmin
mc ls ldp/
```

**Rollback**: Revert Terraform change and re-apply

---

### Phase 3: PyIceberg Update (MEDIUM RISK)

**Goal**: Update PyIceberg for better Iceberg support

**Updates**:
```yaml
# docker/spark/requirements.txt
pyiceberg[s3fs]: 0.6.1 → 0.10.0
```

**Prerequisites**:
- Keep PySpark at 3.5.0 for this phase
- OR upgrade to PySpark 4.0.1 simultaneously (see Phase 5)

**Steps**:
1. Update pyiceberg version
2. Test Iceberg table operations
3. Verify S3/MinIO integration

**Testing**:
- Create Iceberg tables
- Read/write operations
- Table maintenance operations
- Verify metadata compatibility

**Known Issues**:
- May require fsspec version adjustments
- Test with existing Iceberg tables

---

### Phase 4: Terraform Provider Migration (HIGH RISK - REQUIRES PLANNING)

**Goal**: Migrate to Terraform Kubernetes Provider v3 and Helm Provider v3

⚠️ **This is a major code change. Do NOT attempt without dedicated time and testing.**

**Code Changes Required**:

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

### Phase 5: PySpark 4.0 Migration (HIGH RISK)

**Goal**: Upgrade to PySpark 4.0 for performance improvements

⚠️ **Prerequisites**:
- Python >= 3.10 in Docker base images
- Apache Iceberg supports only Spark 4.0, NOT 4.1

**Updates Required**:

1. **Spark Requirements** (`docker/spark/requirements.txt`):
```yaml
# Current
pyspark==3.5.0

# New
pyspark==4.0.1  # NOT 4.1.0 due to Iceberg compatibility
```

2. **Jupyter Requirements** (`docker/jupyter/requirements.txt`):
```yaml
pyspark==4.0.1
```

3. **Spark Docker Base Image** (`docker/spark/Dockerfile`):
```dockerfile
# Current
FROM apache/spark:3.5.0-python3

# New
FROM apache/spark:4.0.1-python3
```

4. **Jupyter Spark Packages** (`docker/jupyter/Dockerfile`):
```dockerfile
# Current
ENV PYSPARK_SUBMIT_ARGS="--packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.0,org.apache.hadoop:hadoop-aws:3.3.4 pyspark-shell"

# New
ENV PYSPARK_SUBMIT_ARGS="--packages org.apache.iceberg:iceberg-spark-runtime-4.0_2.13:1.10.0,org.apache.hadoop:hadoop-aws:3.4.1 pyspark-shell"
```

**Breaking Changes**:
- Python >= 3.10 required
- Scala version changes (2.12 → 2.13)
- API changes in PySpark 4.0
- Iceberg runtime JAR version change

**Testing Checklist**:
- [ ] Spark master/worker start correctly
- [ ] Spark UI accessible
- [ ] Submit test Spark job
- [ ] Read/write to MinIO
- [ ] Iceberg table operations
- [ ] Jupyter can connect to Spark
- [ ] Run existing Airflow + Spark DAGs
- [ ] Performance benchmarks

**Rollback**:
- Revert Docker image changes
- Rebuild images
- Redeploy

**Time Estimate**: 4-8 hours for migration + comprehensive testing

---

### Phase 6: NumPy 2.x + PyArrow Major Update (HIGHEST RISK)

**Goal**: Update to latest NumPy and PyArrow

⚠️ **WARNING**: NumPy 2.x has breaking changes. Do this LAST after everything else is stable.

**Updates**:
```yaml
# All requirements.txt files
numpy: 1.26.3 → 2.3.5
pyarrow: 14.0.2 → 22.0.0
```

**Known Breaking Changes**:
- NumPy 2.x dtype changes
- NumPy 2.x removed deprecated APIs
- PyArrow 22.x may have schema compatibility issues

**Compatibility Testing Required**:
- Pandas with NumPy 2.x
- PyArrow with NumPy 2.x
- PySpark with PyArrow 22.x
- Iceberg with PyArrow 22.x

**Recommendation**:
- Consider skipping this update until you have specific needs
- OR wait for ecosystem to stabilize around NumPy 2.x
- Current versions (1.26.3, 14.0.2) are stable and widely compatible

**Testing**:
- Run ALL existing pipelines
- Verify data integrity
- Check for deprecation warnings
- Performance testing

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

| Update | Benefit | Risk | Effort | Priority |
|--------|---------|------|--------|----------|
| pandas 2.3.3 | Bug fixes, minor features | 🟢 Low | 🟢 Low | ✅ HIGH |
| jupyterlab 4.5.1 | UI improvements | 🟢 Low | 🟢 Low | ✅ HIGH |
| MinIO 5.4.0 | Bug fixes | 🟡 Medium | 🟢 Low | ✅ MEDIUM |
| PyIceberg 0.10.0 | Better Iceberg support | 🟡 Medium | 🟡 Medium | 🟡 MEDIUM |
| Terraform v3 | Future compatibility | 🔴 High | 🔴 High | ❌ LOW |
| PySpark 4.0 | Performance, features | 🔴 High | 🔴 High | 🟡 MEDIUM |
| NumPy 2.x | Future compatibility | 🔴 High | 🟠 Medium | ❌ LOW |
| PyArrow 22.x | Performance, features | 🔴 High | 🟠 Medium | ❌ LOW |

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

**Document Version**: 1.1
**Last Updated**: 2025-12-19
**Status**: Phase 1 Completed - Ready for Testing
