# LDP Monitoring

This directory contains monitoring configuration and Grafana dashboards for the Local Data Platform.

## Overview

The monitoring stack includes:
- **Prometheus** - Metrics collection and storage
- **Grafana** - Visualization and dashboards

## Accessing Monitoring

### Grafana
```bash
# Port forward Grafana
make grafana-forward

# Open http://localhost:3000
# Default credentials: admin / admin
```

### Prometheus
```bash
# Port forward Prometheus
make prometheus-forward

# Open http://localhost:9090
```

## Available Dashboards

The `dashboards/` directory contains pre-built Grafana dashboards:

| Dashboard | File | Description |
|-----------|------|-------------|
| Platform Overview | `platform-overview.json` | Overall health, CPU, memory across all services |
| Airflow | `airflow.json` | DAG execution, scheduler metrics |
| Spark | `spark.json` | Master/worker status, job metrics |
| MinIO | `minio.json` | Storage metrics, S3 traffic |

## Importing Dashboards

### Option 1: Using the import script
```bash
# Import all dashboards to Grafana
./monitoring/import-dashboards.sh
```

### Option 2: Manual import via Grafana UI
1. Open Grafana at http://localhost:3000
2. Go to **Dashboards** > **Import**
3. Click **Upload JSON file**
4. Select a dashboard file from `monitoring/dashboards/`
5. Click **Import**

### Option 3: Using Grafana API
```bash
# Import a single dashboard
curl -X POST \
  -H "Content-Type: application/json" \
  -d @monitoring/dashboards/platform-overview.json \
  http://admin:admin@localhost:3000/api/dashboards/db
```

## Dashboard Features

### Platform Overview
- Service health status (UP/DOWN indicators)
- CPU usage by service
- Memory usage by service
- Service health over time
- Open file descriptors

### Airflow Dashboard
- Webserver status
- CPU and memory usage
- File descriptors
- Troubleshooting tips panel

### Spark Dashboard
- Master and worker status
- Total cluster CPU/memory
- Per-node resource usage
- Cluster health over time

### MinIO Dashboard
- Storage status
- S3 traffic (send/receive)
- Request rates
- Memory usage

## Prometheus Metrics

Prometheus scrapes metrics from:
- Airflow webserver (port 8080)
- Spark master (port 8080)
- Spark workers (port 8081)
- MinIO (port 9000)
- Kubernetes pods with prometheus annotations

### Useful Prometheus Queries

```promql
# Service health
up

# CPU usage rate
rate(process_cpu_seconds_total[1m])

# Memory usage
process_resident_memory_bytes

# Count healthy services
count(up == 1)
```

## Troubleshooting

### Grafana not showing data
1. Check Prometheus is running: `kubectl get pods -n ldp -l app=prometheus`
2. Verify Prometheus can reach targets: http://localhost:9090/targets
3. Check Grafana datasource: Dashboards > Data Sources > Prometheus

### Prometheus targets down
1. Check target pods are running: `make pods`
2. Verify network connectivity from Prometheus pod
3. Check service endpoints: `kubectl get endpoints -n ldp`

### Dashboards not loading
1. Ensure correct datasource UID (should be "prometheus")
2. Re-import the dashboard
3. Check browser console for errors
