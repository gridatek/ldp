resource "helm_release" "postgresql" {
  name       = "postgresql"
  repository = "https://charts.bitnami.com/bitnami"
  chart      = "postgresql"
  namespace  = var.namespace
  version    = "13.2.24"

  values = [
    <<-EOT
    auth:
      username: ${var.username}
      password: ${var.password}
      database: ${var.database}

    primary:
      persistence:
        enabled: true
        size: ${var.persistence_size}

      service:
        type: NodePort
        nodePorts:
          postgresql: ${var.nodeport}

    resources:
      requests:
        memory: "256Mi"
        cpu: "250m"
    EOT
  ]
}
