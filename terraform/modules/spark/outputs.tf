output "master_service_name" {
  value       = "spark-master-svc"
  description = "Spark master service name"
}

output "master_port" {
  value       = 7077
  description = "Spark master port"
}

output "master_http_port" {
  value       = 8080
  description = "Spark master HTTP port"
}

output "master_nodeport_http" {
  value       = var.master_nodeport_http
  description = "Spark master HTTP NodePort"
}
