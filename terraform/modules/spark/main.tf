resource "helm_release" "spark" {
  name       = "spark"
  repository = "https://charts.bitnami.com/bitnami"
  chart      = "spark"
  namespace  = var.namespace
  version    = "8.1.5"

  values = [
    <<-EOT
    master:
      service:
        type: NodePort
        nodePorts:
          http: ${var.master_nodeport_http}
          cluster: ${var.master_nodeport_cluster}

      resources:
        requests:
          memory: "1Gi"
          cpu: "500m"

    worker:
      replicaCount: ${var.worker_replicas}

      resources:
        requests:
          memory: "1Gi"
          cpu: "500m"

      extraEnvVars:
        - name: SPARK_WORKER_MEMORY
          value: "1G"
        - name: SPARK_WORKER_CORES
          value: "1"

    image:
      registry: docker.io
      repository: spark
      tag: "3.5.5-python3"
      pullPolicy: IfNotPresent
    EOT
  ]
}
