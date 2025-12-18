# Production-Ready Local Deployment Guide

> **⚠️ Important**: This guide covers **production-like practices for LOCAL environments**, not actual production cloud deployment. LDP is designed for local development, testing, and CI/CD - not for production data workloads.

This guide helps you configure LDP with production-ready practices (security, monitoring, testing) while still running locally on Minikube or in CI environments.

## When to Use This Guide

Use this guide if you want to:
- Run LDP with production-like security practices locally
- Set up comprehensive monitoring for local development
- Configure proper backup/recovery for your local environment
- Prepare pipelines for eventual cloud deployment

## For Actual Production

For real production data workloads, use cloud-managed services instead:
- **AWS**: EMR, Glue, MWAA (Managed Airflow), Redshift
- **GCP**: Dataproc, Cloud Composer, BigQuery
- **Azure**: Synapse Analytics, Data Factory, Databricks
- **Multi-cloud**: Databricks, Snowflake, Confluent

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Security Configuration](#security-configuration)
3. [Monitoring Setup](#monitoring-setup)
4. [Data Quality Framework](#data-quality-framework)
5. [Performance Tuning](#performance-tuning)
6. [Backup and Recovery](#backup-and-recovery)
7. [Troubleshooting](#troubleshooting)
8. [Operational Runbook](#operational-runbook)

## Prerequisites

### Hardware Requirements (Production)

| Component | CPU | Memory | Storage |
|-----------|-----|--------|---------|
| Kubernetes Cluster | 8+ cores | 32GB+ | 200GB+ |
| Spark Workers (each) | 4 cores | 8GB | 50GB |
| PostgreSQL | 2 cores | 4GB | 50GB SSD |
| MinIO | 2 cores | 4GB | 500GB+ |

### Software Requirements

- Kubernetes 1.26+
- Terraform 1.5+
- kubectl configured
- Helm 3.x

## Security Configuration

### 1. Secrets Management

The platform uses Kubernetes Secrets for sensitive data. **Never commit credentials to version control.**

#### Using External Secrets (Recommended for Production)

Create a `terraform.tfvars` file (add to `.gitignore`):

```hcl
# terraform.tfvars - DO NOT COMMIT
minio_root_user       = "your-secure-username"
minio_root_password   = "your-secure-password-32chars"
postgresql_username   = "ldp_prod"
postgresql_password   = "your-postgresql-password"
airflow_admin_username = "admin"
airflow_admin_password = "your-airflow-password"
grafana_admin_username = "admin"
grafana_admin_password = "your-grafana-password"
```

#### Environment Variables Alternative

```bash
export TF_VAR_minio_root_password="your-secure-password"
export TF_VAR_postgresql_password="your-postgresql-password"
export TF_VAR_airflow_admin_password="your-airflow-password"
export TF_VAR_grafana_admin_password="your-grafana-password"

terraform apply
```

### 2. Network Security

#### Restrict Service Access

For production, modify services to use `ClusterIP` instead of `NodePort`:

```hcl
# In terraform configuration
spec {
  type = "ClusterIP"  # Instead of NodePort
  ...
}
```

Use an Ingress controller with TLS for external access:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ldp-ingress
  namespace: ldp
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - airflow.yourdomain.com
    secretName: airflow-tls
  rules:
  - host: airflow.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: airflow-webserver
            port:
              number: 8080
```

### 3. RBAC Configuration

Create dedicated service accounts:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: spark-service-account
  namespace: ldp
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: spark-role
  namespace: ldp
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps"]
  verbs: ["get", "list", "watch", "create", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: spark-role-binding
  namespace: ldp
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: spark-role
subjects:
- kind: ServiceAccount
  name: spark-service-account
  namespace: ldp
```

## Monitoring Setup

### Enable Monitoring Stack

Set `enable_monitoring = true` in your Terraform configuration (enabled by default):

```hcl
variable "enable_monitoring" {
  default = true
}
```

### Access Monitoring Services

After deployment:

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| Prometheus | http://\<node-ip\>:30909 | N/A |
| Grafana | http://\<node-ip\>:30300 | admin/admin |

### Key Metrics to Monitor

#### Pipeline Metrics
- `pipeline_duration_seconds` - Total pipeline execution time
- `pipeline_stage_duration_seconds` - Individual stage durations
- `pipeline_stage_input_rows` - Input row counts
- `pipeline_stage_output_rows` - Output row counts
- `pipeline_runs_total` - Total pipeline runs by status

#### Infrastructure Metrics
- `up` - Service availability
- `process_cpu_seconds_total` - CPU usage
- `process_resident_memory_bytes` - Memory usage

### Creating Custom Dashboards

Import the pre-configured dashboard or create custom ones in Grafana:

1. Navigate to Grafana → Dashboards → Import
2. Upload the JSON from `terraform/modules/monitoring/dashboards/`
3. Select Prometheus as the data source

### Alerting Configuration

Create alert rules in Prometheus for critical conditions:

```yaml
groups:
- name: ldp-alerts
  rules:
  - alert: PipelineFailure
    expr: increase(pipeline_runs_total{status="failed"}[5m]) > 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Pipeline failure detected"

  - alert: HighPipelineDuration
    expr: pipeline_duration_seconds > 3600
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Pipeline running longer than 1 hour"

  - alert: ServiceDown
    expr: up == 0
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Service {{ $labels.job }} is down"
```

## Data Quality Framework

### Using the Data Quality Validator

The platform includes a comprehensive data quality framework:

```python
from lib.data_quality import DataQualityValidator, ValidationRule

# Create validator
validator = DataQualityValidator(df, "sales_data")

# Add validation rules
validator.add_rule(ValidationRule.not_null("customer_id"))
validator.add_rule(ValidationRule.unique("order_id"))
validator.add_rule(ValidationRule.in_range("amount", min_val=0, max_val=1000000))
validator.add_rule(ValidationRule.matches_pattern("email", r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"))
validator.add_rule(ValidationRule.in_set("status", {"pending", "completed", "cancelled"}))

# Run validation
report = validator.validate()

if not report.is_valid:
    for error in report.errors:
        print(f"Validation failed: {error.rule_name} - {error.message}")
    raise ValueError("Data quality checks failed")
```

### Available Validation Rules

| Rule | Description | Parameters |
|------|-------------|------------|
| `not_null` | Check for null values | column, threshold |
| `unique` | Check uniqueness | column |
| `in_range` | Validate numeric range | column, min_val, max_val |
| `not_empty` | Check for empty strings | column |
| `matches_pattern` | Regex pattern matching | column, pattern |
| `in_set` | Validate against allowed values | column, valid_values |
| `row_count` | Validate row count | min_count, max_count, exact_count |
| `column_exists` | Check required columns | columns |
| `no_duplicates` | Check for duplicate rows | columns |
| `custom` | Custom validation logic | name, check_fn, message |

### Generating Data Quality Profiles

```python
from lib.data_quality import DataQualityProfile

profile = DataQualityProfile.profile(df)
print(f"Total rows: {profile['total_rows']}")
print(f"Columns: {profile['total_columns']}")

for col, stats in profile['columns'].items():
    print(f"{col}: {stats['null_percentage']}% null, {stats['approx_distinct_count']} distinct")
```

## Performance Tuning

### Spark Configuration

Optimize Spark for production workloads:

```python
spark = SparkSession.builder \
    .appName("ProductionJob") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.executor.memory", "4g") \
    .config("spark.executor.cores", "2") \
    .config("spark.driver.memory", "2g") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .getOrCreate()
```

### Iceberg Table Maintenance

Schedule regular maintenance jobs:

```python
# Expire old snapshots (keep last 7 days)
spark.sql(f"""
    CALL local.system.expire_snapshots(
        table => 'db.my_table',
        older_than => TIMESTAMP '{datetime.now() - timedelta(days=7)}'
    )
""")

# Remove orphan files
spark.sql(f"""
    CALL local.system.remove_orphan_files(
        table => 'db.my_table'
    )
""")

# Compact small files
spark.sql(f"""
    CALL local.system.rewrite_data_files(
        table => 'db.my_table',
        options => map('target-file-size-bytes', '134217728')
    )
""")
```

### Resource Scaling

Scale Spark workers based on workload:

```bash
# Scale to 5 workers
kubectl scale deployment spark-worker -n ldp --replicas=5

# Enable autoscaling
kubectl autoscale deployment spark-worker -n ldp \
  --min=2 --max=10 --cpu-percent=70
```

## Backup and Recovery

### PostgreSQL Backup

Create regular backups of the metadata store:

```bash
# Manual backup
kubectl exec -n ldp postgresql-0 -- \
  pg_dump -U ldp metastore > backup_$(date +%Y%m%d).sql

# Automated backup CronJob
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: ldp
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15
            command:
            - /bin/sh
            - -c
            - pg_dump -h postgresql -U ldp metastore | gzip > /backups/backup_$(date +%Y%m%d).sql.gz
            volumeMounts:
            - name: backup-storage
              mountPath: /backups
          restartPolicy: OnFailure
```

### MinIO Backup

Use MinIO client for data backup:

```bash
# Sync to backup location
mc mirror ldp/datalake backup/datalake --preserve

# Scheduled backup script
#!/bin/bash
mc mirror ldp/datalake s3/backup-bucket/ldp-$(date +%Y%m%d) --preserve
mc mirror ldp/warehouse s3/backup-bucket/warehouse-$(date +%Y%m%d) --preserve
```

### Disaster Recovery

1. **Regular backups** of PostgreSQL metadata
2. **MinIO replication** to secondary storage
3. **Terraform state backup** to remote backend
4. **Document recovery procedures** and test regularly

## Troubleshooting

### Common Issues

#### Pods Not Starting
```bash
# Check events
kubectl get events -n ldp --sort-by='.lastTimestamp' | tail -20

# Check resource constraints
kubectl describe nodes | grep -A5 "Allocated resources"

# Check pod logs
kubectl logs -n ldp <pod-name> --previous
```

#### Spark Jobs Failing
```bash
# Check Spark UI for job details
kubectl port-forward -n ldp svc/spark-master-svc 8080:8080

# Check driver logs
kubectl logs -n ldp -l spark-role=driver

# Check executor logs
kubectl logs -n ldp -l spark-role=executor
```

#### MinIO Connection Issues
```bash
# Verify MinIO is running
kubectl get pods -n ldp -l app=minio

# Test connectivity from within cluster
kubectl run -it --rm debug --image=minio/mc --restart=Never -- \
  mc alias set test http://minio:9000 admin minioadmin && mc ls test/
```

#### Airflow DAG Issues
```bash
# Check scheduler logs
kubectl logs -n ldp -l component=scheduler --tail=100

# Test DAG syntax
kubectl exec -n ldp deployment/airflow-webserver -- \
  airflow dags test <dag_id> 2024-01-01
```

## Operational Runbook

### Daily Operations

1. **Check service health**
   ```bash
   kubectl get pods -n ldp
   ```

2. **Review pipeline runs**
   - Access Airflow UI and check DAG runs
   - Review failed tasks and logs

3. **Monitor metrics**
   - Check Grafana dashboards
   - Review Prometheus alerts

### Weekly Operations

1. **Run Iceberg maintenance**
   - Expire old snapshots
   - Remove orphan files
   - Compact data files

2. **Review resource usage**
   ```bash
   kubectl top pods -n ldp
   kubectl top nodes
   ```

3. **Check storage capacity**
   ```bash
   mc admin info ldp/
   ```

### Monthly Operations

1. **Test disaster recovery procedures**
2. **Review and rotate credentials**
3. **Update documentation**
4. **Review and tune performance**
5. **Audit security configurations**

### Incident Response

1. **Identify** - Use monitoring to identify the issue
2. **Triage** - Determine severity and impact
3. **Communicate** - Notify stakeholders
4. **Resolve** - Apply fix or workaround
5. **Document** - Record incident details and resolution
6. **Review** - Conduct post-incident review

## Additional Resources

- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Spark Performance Tuning](https://spark.apache.org/docs/latest/tuning.html)
- [Iceberg Performance](https://iceberg.apache.org/docs/latest/performance/)
- [Prometheus Alerting](https://prometheus.io/docs/alerting/latest/overview/)
