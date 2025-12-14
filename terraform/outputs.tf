output "platform_info" {
  value = {
    namespace = kubernetes_namespace.ldp.metadata[0].name
    services = {
      airflow = {
        url      = "http://$(minikube ip):30080"
        username = var.airflow_admin_username
        password = var.airflow_admin_password
      }
      minio = {
        console_url = "http://$(minikube ip):30901"
        api_url     = "http://$(minikube ip):30900"
        username    = var.minio_root_user
        password    = var.minio_root_password
      }
      spark = {
        master_url = "http://$(minikube ip):30707"
      }
      jupyter = {
        url = "http://$(minikube ip):30888"
      }
      postgresql = {
        host     = "postgresql"
        port     = 5432
        database = var.postgresql_database
        username = var.postgresql_username
        password = var.postgresql_password
      }
    }
  }
  description = "Information about deployed platform services"
  sensitive   = true
}

output "namespace" {
  value       = kubernetes_namespace.ldp.metadata[0].name
  description = "The Kubernetes namespace where the platform is deployed"
}
