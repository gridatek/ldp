resource "helm_release" "airflow" {
  name       = "airflow"
  repository = "https://airflow.apache.org"
  chart      = "airflow"
  namespace  = var.namespace
  version    = "1.18.0"

  values = [
    <<-EOT
    executor: "KubernetesExecutor"

    airflowVersion: "3.0.2"

    defaultAirflowRepository: apache/airflow
    defaultAirflowTag: "3.0.2"

    webserver:
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

    apiServer:
      replicas: 1
      allowPodLogReading: true

    migrateDatabaseJob:
      enabled: true
      useHelmHooks: false
      applyCustomEnv: false
      ttlSecondsAfterFinished: 300

    createUserJob:
      useHelmHooks: false
      applyCustomEnv: false
      ttlSecondsAfterFinished: 300

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

  timeout = 900  # Increased for CI environment (15 minutes)
  wait = true
  wait_for_jobs = true
}
