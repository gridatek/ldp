output "webserver_service_name" {
  value       = "airflow-webserver"
  description = "Airflow webserver service name"
}

output "webserver_port" {
  value       = 8080
  description = "Airflow webserver port"
}

output "webserver_nodeport" {
  value       = var.webserver_nodeport
  description = "Airflow webserver NodePort"
}
