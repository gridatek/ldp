output "prometheus_url" {
  description = "URL to access Prometheus"
  value       = "http://localhost:30909"
}

output "grafana_url" {
  description = "URL to access Grafana"
  value       = "http://localhost:30300"
}

output "prometheus_service_name" {
  description = "Prometheus service name"
  value       = kubernetes_service.prometheus.metadata[0].name
}

output "grafana_service_name" {
  description = "Grafana service name"
  value       = kubernetes_service.grafana.metadata[0].name
}
