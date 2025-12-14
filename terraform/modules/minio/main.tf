resource "helm_release" "minio" {
  name       = "minio"
  repository = "https://charts.min.io/"
  chart      = "minio"
  namespace  = var.namespace
  version    = "5.0.14"

  values = [
    <<-EOT
    replicas: 1
    mode: standalone
    rootUser: ${var.root_user}
    rootPassword: ${var.root_password}

    persistence:
      enabled: true
      size: ${var.persistence_size}

    service:
      type: NodePort
      port: 9000
      nodePort: ${var.api_nodeport}

    consoleService:
      type: NodePort
      port: 9001
      nodePort: ${var.console_nodeport}

    resources:
      requests:
        memory: "512Mi"
        cpu: "250m"

    buckets:
      - name: warehouse
        policy: none
        purge: false
      - name: datalake
        policy: none
        purge: false
    EOT
  ]
}
