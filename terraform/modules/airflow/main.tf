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

    # API Server configuration for Airflow 3.0
    apiServer:
      service:
        type: NodePort
        ports:
          - name: api-server
            port: 9091
            nodePort: ${var.webserver_nodeport}

    # Webserver configuration (still used for UI and default user)
    webserver:
      defaultUser:
        enabled: true
        username: ${var.admin_username}
        password: ${var.admin_password}
        email: admin@ldp.local
        firstName: Admin
        lastName: User
        role: Admin

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

    dags:
      persistence:
        enabled: true
        size: ${var.dags_persistence_size}

    logs:
      persistence:
        enabled: true
        size: ${var.logs_persistence_size}

    env:
      - name: AIRFLOW__CORE__LOAD_EXAMPLES
        value: "False"
      - name: AIRFLOW__WEBSERVER__EXPOSE_CONFIG
        value: "True"
    EOT
  ]

  timeout = 600
}
