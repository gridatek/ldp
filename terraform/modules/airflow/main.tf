resource "helm_release" "airflow" {
  name       = "airflow"
  repository = "https://airflow.apache.org"
  chart      = "airflow"
  namespace  = var.namespace
  version    = "1.17.0"

  values = [
    <<-EOT
    executor: "KubernetesExecutor"

    airflowVersion: "3.0.0"

    defaultAirflowRepository: apache/airflow
    defaultAirflowTag: "3.0.0"

    # Webserver configuration
    webserver:
      replicas: 1
      service:
        type: NodePort
        ports:
          - name: airflow-ui
            port: 8080
            nodePort: ${var.webserver_nodeport}
      defaultUser:
        enabled: true
        username: ${var.admin_username}
        password: ${var.admin_password}
        email: admin@ldp.local
        firstName: Admin
        lastName: User
        role: Admin
      resources:
        requests:
          cpu: 100m
          memory: 256Mi

    # Scheduler configuration
    scheduler:
      replicas: 1
      resources:
        requests:
          cpu: 100m
          memory: 256Mi

    # Triggerer configuration
    triggerer:
      enabled: false

    # Disable flower
    flower:
      enabled: false

    # Disable statsd
    statsd:
      enabled: false

    # Use external PostgreSQL
    postgresql:
      enabled: false

    data:
      metadataConnection:
        user: ${var.postgresql_user}
        pass: ${var.postgresql_pass}
        protocol: postgresql
        host: ${var.postgresql_host}
        port: ${var.postgresql_port}
        db: ${var.postgresql_db}

    # Disable persistence for CI environments
    dags:
      persistence:
        enabled: false
      gitSync:
        enabled: false

    logs:
      persistence:
        enabled: false

    # Disable migrations job wait (handled separately)
    migrateDatabaseJob:
      enabled: false

    # Environment variables
    env:
      - name: AIRFLOW__CORE__LOAD_EXAMPLES
        value: "False"
      - name: AIRFLOW__WEBSERVER__EXPOSE_CONFIG
        value: "True"
    EOT
  ]

  timeout = 600
  wait    = false
}
