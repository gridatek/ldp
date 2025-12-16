# Local Data Platform - Troubleshooting Guide

This guide helps you diagnose and fix common issues when running the Local Data Platform for prototyping and testing.

## Quick Diagnostics

Run these commands first to get an overview of your platform status:

```bash
# Full health check
make health

# Quick pod status
make pods

# View all services
make services

# Run interactive troubleshooting
./scripts/troubleshoot.sh
```

## Common Issues

### 1. Platform Won't Start

#### Symptoms
- `make start` fails
- Terraform errors
- Pods stuck in `Pending` or `ContainerCreating`

#### Solutions

**Check Minikube is running:**
```bash
minikube status

# If not running, start it:
minikube start --memory=8192 --cpus=4
```

**Check available resources:**
```bash
# Minikube needs at least 8GB RAM and 4 CPUs
minikube config view

# Check node resources
kubectl describe node minikube | grep -A 5 "Allocated resources"
```

**Re-initialize Terraform:**
```bash
cd terraform
terraform init -reconfigure
terraform apply
```

---

### 2. Pods Not Running

#### Check pod status
```bash
kubectl get pods -n ldp

# Describe a specific pod for details
kubectl describe pod <pod-name> -n ldp

# Common states:
# - Pending: Resource constraints or scheduling issues
# - ImagePullBackOff: Can't pull Docker image
# - CrashLoopBackOff: Container keeps crashing
# - ContainerCreating: Still initializing
```

#### Pod stuck in Pending
```bash
# Check events
kubectl get events -n ldp --sort-by='.lastTimestamp'

# Check PVC status (storage issues)
kubectl get pvc -n ldp

# Check if PVs are available
kubectl get pv
```

#### Pod in CrashLoopBackOff
```bash
# View pod logs
kubectl logs <pod-name> -n ldp

# View previous container logs (if restarted)
kubectl logs <pod-name> -n ldp --previous

# Check resource limits
kubectl describe pod <pod-name> -n ldp | grep -A 10 "Limits:"
```

---

### 3. Airflow Issues

#### Webserver not accessible
```bash
# Check if webserver pod is running
kubectl get pods -n ldp -l component=webserver

# View webserver logs
kubectl logs -n ldp -l component=webserver

# Port forward manually
kubectl port-forward -n ldp svc/airflow-webserver 8080:8080
```

#### DAGs not appearing
```bash
# Check scheduler logs
kubectl logs -n ldp -l component=scheduler

# Verify DAG files are mounted
kubectl exec -n ldp <scheduler-pod> -- ls /opt/airflow/dags/

# Trigger DAG refresh
kubectl exec -n ldp <webserver-pod> -- airflow dags reserialize
```

#### Database connection errors
```bash
# Check PostgreSQL is running
kubectl get pods -n ldp -l app=postgresql

# Test database connection
kubectl exec -n ldp <airflow-pod> -- \
  python -c "from airflow.settings import engine; print(engine.execute('SELECT 1').fetchone())"
```

#### Scheduler not processing tasks
```bash
# Restart scheduler
kubectl rollout restart deployment/airflow-scheduler -n ldp

# Check scheduler health
kubectl exec -n ldp <scheduler-pod> -- airflow jobs check --job-type SchedulerJob
```

---

### 4. Spark Issues

#### Master not reachable
```bash
# Check master pod
kubectl get pods -n ldp -l app=spark-master

# View master logs
kubectl logs -n ldp -l app=spark-master

# Access Spark UI
kubectl port-forward -n ldp svc/spark-master-svc 8080:8080
```

#### Workers not connecting
```bash
# Check worker pods
kubectl get pods -n ldp -l app=spark-worker

# View worker logs
kubectl logs -n ldp -l app=spark-worker

# Verify network connectivity
kubectl exec -n ldp <worker-pod> -- ping -c 3 spark-master
```

#### Job submission failures
```bash
# Submit a test job
kubectl exec -n ldp <spark-master-pod> -- \
  spark-submit --master spark://spark-master:7077 \
  /opt/spark/examples/src/main/python/pi.py 10

# Common issues:
# - Out of memory: Increase executor memory
# - Class not found: Check PYTHONPATH and dependencies
# - Connection refused: Master might be starting up
```

#### Out of memory errors
```bash
# Check resource usage
kubectl top pods -n ldp -l app=spark-worker

# Adjust Spark memory settings in spark-defaults.conf:
# spark.executor.memory=2g
# spark.driver.memory=1g
```

---

### 5. MinIO Issues

#### Connection refused
```bash
# Check MinIO pod
kubectl get pods -n ldp -l app=minio

# View MinIO logs
kubectl logs -n ldp -l app=minio

# Access MinIO console
kubectl port-forward -n ldp svc/minio-console 9001:9001
```

#### Access denied / Authentication errors
```bash
# Check credentials in secret
kubectl get secret -n ldp minio-credentials -o jsonpath='{.data.root-user}' | base64 -d
kubectl get secret -n ldp minio-credentials -o jsonpath='{.data.root-password}' | base64 -d

# Default credentials: admin / minioadmin
```

#### Bucket not found
```bash
# Initialize buckets
make init-minio

# List existing buckets
kubectl exec -n ldp <minio-pod> -- mc ls local/

# Create bucket manually
kubectl exec -n ldp <minio-pod> -- mc mb local/my-bucket
```

#### Storage full
```bash
# Check storage usage
kubectl exec -n ldp <minio-pod> -- df -h /data

# Check PVC usage
kubectl describe pvc -n ldp minio-pvc
```

---

### 6. PostgreSQL Issues

#### Database unreachable
```bash
# Check PostgreSQL pod
kubectl get pods -n ldp -l app=postgresql

# View logs
kubectl logs -n ldp -l app=postgresql

# Test connection
kubectl exec -n ldp <postgres-pod> -- psql -U airflow -d airflow -c "SELECT 1"
```

#### Connection limit reached
```bash
# Check active connections
kubectl exec -n ldp <postgres-pod> -- \
  psql -U airflow -d airflow -c "SELECT count(*) FROM pg_stat_activity"

# Increase max_connections in postgresql.conf if needed
```

---

### 7. Networking Issues

#### Services not accessible
```bash
# Check service endpoints
kubectl get endpoints -n ldp

# Verify service is correctly configured
kubectl describe svc <service-name> -n ldp

# Check NodePort is exposed
kubectl get svc -n ldp -o wide
```

#### Port forwarding issues
```bash
# Kill existing port forwards
pkill -f "kubectl port-forward"

# Try different local port
kubectl port-forward -n ldp svc/airflow-webserver 8081:8080
```

#### DNS resolution problems
```bash
# Test DNS from within a pod
kubectl exec -n ldp <any-pod> -- nslookup minio
kubectl exec -n ldp <any-pod> -- nslookup spark-master
```

---

### 8. Resource Issues

#### Check overall resource usage
```bash
# Node resources
kubectl top nodes

# Pod resources
kubectl top pods -n ldp

# Minikube resources
minikube ssh "free -h && df -h"
```

#### Minikube running out of disk
```bash
# Check disk usage
minikube ssh "df -h"

# Clean up unused images
minikube ssh "docker system prune -a"

# Increase disk size (requires recreate)
minikube delete
minikube start --disk-size=50g --memory=8192 --cpus=4
```

#### Increase Minikube resources
```bash
# Stop minikube
minikube stop

# Reconfigure
minikube config set memory 12288
minikube config set cpus 6

# Start again
minikube start
```

---

## Monitoring Access

### Accessing Grafana Dashboards
```bash
# Port forward Grafana
kubectl port-forward -n ldp svc/grafana 3000:3000

# Open http://localhost:3000
# Default credentials: admin / admin
```

### Accessing Prometheus
```bash
# Port forward Prometheus
kubectl port-forward -n ldp svc/prometheus 9090:9090

# Open http://localhost:9090
```

### Available Dashboards
- **LDP - Platform Overview**: Overall health and resource usage
- **LDP - Airflow**: DAG execution and scheduler metrics
- **LDP - Spark**: Job execution and cluster health
- **LDP - MinIO Storage**: S3 traffic and storage metrics

---

## Logs and Debugging

### View logs for all components
```bash
# Airflow logs
kubectl logs -n ldp -l app.kubernetes.io/name=airflow --all-containers -f

# Spark logs
kubectl logs -n ldp -l app=spark-master -f
kubectl logs -n ldp -l app=spark-worker -f

# MinIO logs
kubectl logs -n ldp -l app=minio -f

# PostgreSQL logs
kubectl logs -n ldp -l app=postgresql -f
```

### Interactive debugging
```bash
# Shell into a pod
kubectl exec -it <pod-name> -n ldp -- /bin/bash

# Run Python interactively in Airflow
kubectl exec -it <airflow-pod> -n ldp -- python

# Run Spark shell
kubectl exec -it <spark-master-pod> -n ldp -- spark-shell
```

### Export logs for analysis
```bash
# Export all logs to files
./scripts/troubleshoot.sh --export-logs

# Logs will be saved to ./logs/ directory
```

---

## Reset and Recovery

### Restart individual components
```bash
# Restart Airflow
kubectl rollout restart deployment/airflow-webserver -n ldp
kubectl rollout restart deployment/airflow-scheduler -n ldp

# Restart Spark
kubectl rollout restart deployment/spark-master -n ldp
kubectl rollout restart deployment/spark-worker -n ldp

# Restart MinIO
kubectl rollout restart statefulset/minio -n ldp
```

### Full platform restart
```bash
# Stop everything
make stop

# Start again
make start

# Or use Terraform directly
cd terraform
terraform destroy -auto-approve
terraform apply -auto-approve
```

### Complete cleanup and fresh start
```bash
# Full cleanup including Minikube
make cleanup

# Fresh setup
make setup
make start
make init-minio
```

---

## Performance Tips

### For faster local development
1. Reduce Spark worker count to 1
2. Lower memory limits for non-essential services
3. Use local file system instead of MinIO for quick tests
4. Disable monitoring if not needed

### Recommended Minikube settings for LDP
```bash
minikube start \
  --memory=8192 \
  --cpus=4 \
  --disk-size=50g \
  --driver=docker
```

---

## Getting Help

If you're still stuck:

1. Check recent events: `kubectl get events -n ldp --sort-by='.lastTimestamp' | tail -20`
2. Run full diagnostics: `./scripts/troubleshoot.sh --full`
3. Export logs and platform state for analysis
4. Check the project issues on GitHub

---

## Quick Reference

| Service | Port Forward Command | Local URL |
|---------|---------------------|-----------|
| Airflow | `make airflow-forward` | http://localhost:8080 |
| MinIO Console | `make minio-forward` | http://localhost:9001 |
| Spark UI | `make spark-forward` | http://localhost:8080 |
| Jupyter | `make jupyter-forward` | http://localhost:8888 |
| Grafana | `kubectl port-forward -n ldp svc/grafana 3000:3000` | http://localhost:3000 |
| Prometheus | `kubectl port-forward -n ldp svc/prometheus 9090:9090` | http://localhost:9090 |
