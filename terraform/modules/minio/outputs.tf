output "service_name" {
  value       = "minio"
  description = "MinIO service name"
}

output "api_port" {
  value       = 9000
  description = "MinIO API port"
}

output "console_port" {
  value       = 9001
  description = "MinIO Console port"
}

output "api_nodeport" {
  value       = var.api_nodeport
  description = "MinIO API NodePort"
}

output "console_nodeport" {
  value       = var.console_nodeport
  description = "MinIO Console NodePort"
}
