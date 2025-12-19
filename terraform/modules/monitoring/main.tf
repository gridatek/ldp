# Prometheus deployment for metrics collection
resource "kubernetes_deployment_v1" "prometheus" {
  metadata {
    name      = "prometheus"
    namespace = var.namespace
    labels = {
      app = "prometheus"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "prometheus"
      }
    }

    template {
      metadata {
        labels = {
          app = "prometheus"
        }
      }

      spec {
        enable_service_links = false

        container {
          name  = "prometheus"
          image = "prom/prometheus:v2.47.0"

          port {
            container_port = 9090
            name           = "http"
          }

          args = [
            "--config.file=/etc/prometheus/prometheus.yml",
            "--storage.tsdb.path=/prometheus",
            "--web.console.libraries=/etc/prometheus/console_libraries",
            "--web.console.templates=/etc/prometheus/consoles",
            "--web.enable-lifecycle",
          ]

          volume_mount {
            name       = "prometheus-config"
            mount_path = "/etc/prometheus"
          }

          volume_mount {
            name       = "prometheus-data"
            mount_path = "/prometheus"
          }

          resources {
            requests = {
              memory = "512Mi"
              cpu    = "250m"
            }
            limits = {
              memory = "1Gi"
              cpu    = "500m"
            }
          }

          liveness_probe {
            http_get {
              path = "/-/healthy"
              port = 9090
            }
            initial_delay_seconds = 30
            period_seconds        = 15
          }

          readiness_probe {
            http_get {
              path = "/-/ready"
              port = 9090
            }
            initial_delay_seconds = 5
            period_seconds        = 10
          }
        }

        volume {
          name = "prometheus-config"
          config_map {
            name = kubernetes_config_map_v1.prometheus_config.metadata[0].name
          }
        }

        volume {
          name = "prometheus-data"
          empty_dir {}
        }
      }
    }
  }
}

resource "kubernetes_service_v1" "prometheus" {
  metadata {
    name      = "prometheus"
    namespace = var.namespace
    labels = {
      app = "prometheus"
    }
  }

  spec {
    type = "NodePort"

    selector = {
      app = "prometheus"
    }

    port {
      port        = 9090
      target_port = 9090
      node_port   = 30909
      name        = "http"
    }
  }
}

resource "kubernetes_config_map_v1" "prometheus_config" {
  metadata {
    name      = "prometheus-config"
    namespace = var.namespace
  }

  data = {
    "prometheus.yml" = <<-EOT
      global:
        scrape_interval: 15s
        evaluation_interval: 15s

      alerting:
        alertmanagers:
          - static_configs:
              - targets: []

      rule_files: []

      scrape_configs:
        - job_name: 'prometheus'
          static_configs:
            - targets: ['localhost:9090']

        - job_name: 'airflow'
          static_configs:
            - targets: ['airflow-webserver:8080']
          metrics_path: /metrics

        - job_name: 'spark-master'
          static_configs:
            - targets: ['spark-master:8080']
          metrics_path: /metrics/prometheus

        - job_name: 'spark-workers'
          static_configs:
            - targets: ['spark-worker:8081']
          metrics_path: /metrics/prometheus

        - job_name: 'minio'
          static_configs:
            - targets: ['minio:9000']
          metrics_path: /minio/v2/metrics/cluster

        - job_name: 'kubernetes-pods'
          kubernetes_sd_configs:
            - role: pod
              namespaces:
                names:
                  - ${var.namespace}
          relabel_configs:
            - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
              action: keep
              regex: true
            - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
              action: replace
              target_label: __metrics_path__
              regex: (.+)
            - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
              action: replace
              regex: ([^:]+)(?::\d+)?;(\d+)
              replacement: $1:$2
              target_label: __address__
    EOT
  }
}

# Grafana deployment for visualization
resource "kubernetes_deployment_v1" "grafana" {
  metadata {
    name      = "grafana"
    namespace = var.namespace
    labels = {
      app = "grafana"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "grafana"
      }
    }

    template {
      metadata {
        labels = {
          app = "grafana"
        }
      }

      spec {
        enable_service_links = false

        container {
          name  = "grafana"
          image = "grafana/grafana:10.1.0"

          port {
            container_port = 3000
            name           = "http"
          }

          env {
            name  = "GF_SECURITY_ADMIN_USER"
            value = var.grafana_admin_user
          }

          env {
            name = "GF_SECURITY_ADMIN_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.grafana_secrets.metadata[0].name
                key  = "admin-password"
              }
            }
          }

          env {
            name  = "GF_INSTALL_PLUGINS"
            value = "grafana-piechart-panel,grafana-clock-panel"
          }

          volume_mount {
            name       = "grafana-datasources"
            mount_path = "/etc/grafana/provisioning/datasources"
          }

          volume_mount {
            name       = "grafana-dashboards-config"
            mount_path = "/etc/grafana/provisioning/dashboards"
          }

          volume_mount {
            name       = "grafana-dashboards"
            mount_path = "/var/lib/grafana/dashboards"
          }

          resources {
            requests = {
              memory = "256Mi"
              cpu    = "100m"
            }
            limits = {
              memory = "512Mi"
              cpu    = "250m"
            }
          }

          liveness_probe {
            http_get {
              path = "/api/health"
              port = 3000
            }
            initial_delay_seconds = 60
            period_seconds        = 10
          }

          readiness_probe {
            http_get {
              path = "/api/health"
              port = 3000
            }
            initial_delay_seconds = 5
            period_seconds        = 10
          }
        }

        volume {
          name = "grafana-datasources"
          config_map {
            name = kubernetes_config_map_v1.grafana_datasources.metadata[0].name
          }
        }

        volume {
          name = "grafana-dashboards-config"
          config_map {
            name = kubernetes_config_map_v1.grafana_dashboards_config.metadata[0].name
          }
        }

        volume {
          name = "grafana-dashboards"
          config_map {
            name = kubernetes_config_map_v1.grafana_dashboards.metadata[0].name
          }
        }
      }
    }
  }
}

resource "kubernetes_service_v1" "grafana" {
  metadata {
    name      = "grafana"
    namespace = var.namespace
    labels = {
      app = "grafana"
    }
  }

  spec {
    type = "NodePort"

    selector = {
      app = "grafana"
    }

    port {
      port        = 3000
      target_port = 3000
      node_port   = 30300
      name        = "http"
    }
  }
}

resource "kubernetes_secret_v1" "grafana_secrets" {
  metadata {
    name      = "grafana-secrets"
    namespace = var.namespace
  }

  data = {
    "admin-password" = var.grafana_admin_password
  }

  type = "Opaque"
}

resource "kubernetes_config_map_v1" "grafana_datasources" {
  metadata {
    name      = "grafana-datasources"
    namespace = var.namespace
  }

  data = {
    "datasources.yaml" = <<-EOT
      apiVersion: 1
      datasources:
        - name: Prometheus
          type: prometheus
          access: proxy
          url: http://prometheus:9090
          isDefault: true
          editable: false
    EOT
  }
}

resource "kubernetes_config_map_v1" "grafana_dashboards_config" {
  metadata {
    name      = "grafana-dashboards-config"
    namespace = var.namespace
  }

  data = {
    "dashboards.yaml" = <<-EOT
      apiVersion: 1
      providers:
        - name: 'default'
          orgId: 1
          folder: ''
          type: file
          disableDeletion: false
          editable: true
          options:
            path: /var/lib/grafana/dashboards
    EOT
  }
}

resource "kubernetes_config_map_v1" "grafana_dashboards" {
  metadata {
    name      = "grafana-dashboards"
    namespace = var.namespace
  }

  data = {
    "data-platform-overview.json" = <<-EOT
      {
        "annotations": {
          "list": []
        },
        "editable": true,
        "fiscalYearStartMonth": 0,
        "graphTooltip": 0,
        "id": null,
        "links": [],
        "liveNow": false,
        "panels": [
          {
            "datasource": {
              "type": "prometheus",
              "uid": "prometheus"
            },
            "fieldConfig": {
              "defaults": {
                "color": {
                  "mode": "palette-classic"
                },
                "mappings": [],
                "thresholds": {
                  "mode": "absolute",
                  "steps": [
                    {"color": "green", "value": null},
                    {"color": "red", "value": 80}
                  ]
                }
              }
            },
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
            "id": 1,
            "options": {
              "orientation": "auto",
              "reduceOptions": {
                "calcs": ["lastNotNull"],
                "fields": "",
                "values": false
              },
              "showThresholdLabels": false,
              "showThresholdMarkers": true
            },
            "pluginVersion": "10.1.0",
            "targets": [
              {
                "expr": "up",
                "legendFormat": "{{job}}",
                "refId": "A"
              }
            ],
            "title": "Service Health",
            "type": "gauge"
          },
          {
            "datasource": {
              "type": "prometheus",
              "uid": "prometheus"
            },
            "fieldConfig": {
              "defaults": {
                "color": {"mode": "palette-classic"},
                "custom": {
                  "axisCenteredZero": false,
                  "axisLabel": "",
                  "axisPlacement": "auto",
                  "barAlignment": 0,
                  "drawStyle": "line",
                  "fillOpacity": 10,
                  "gradientMode": "none",
                  "lineWidth": 1,
                  "pointSize": 5,
                  "showPoints": "never",
                  "spanNulls": false,
                  "stacking": {"group": "A", "mode": "none"}
                },
                "mappings": [],
                "thresholds": {
                  "mode": "absolute",
                  "steps": [{"color": "green", "value": null}]
                }
              }
            },
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
            "id": 2,
            "options": {"legend": {"calcs": [], "displayMode": "list", "placement": "bottom"}},
            "targets": [
              {
                "expr": "rate(process_cpu_seconds_total[5m])",
                "legendFormat": "{{job}}",
                "refId": "A"
              }
            ],
            "title": "CPU Usage",
            "type": "timeseries"
          }
        ],
        "refresh": "30s",
        "schemaVersion": 38,
        "style": "dark",
        "tags": ["data-platform"],
        "templating": {"list": []},
        "time": {"from": "now-1h", "to": "now"},
        "title": "Data Platform Overview",
        "uid": "data-platform-overview",
        "version": 1,
        "weekStart": ""
      }
    EOT
  }
}
