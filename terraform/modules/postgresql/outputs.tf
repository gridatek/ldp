output "service_name" {
  value       = "postgresql"
  description = "PostgreSQL service name"
}

output "port" {
  value       = 5432
  description = "PostgreSQL port"
}

output "nodeport" {
  value       = var.nodeport
  description = "PostgreSQL NodePort"
}
