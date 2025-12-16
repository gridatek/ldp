variable "namespace" {
  description = "Kubernetes namespace for monitoring components"
  type        = string
}

variable "grafana_admin_user" {
  description = "Grafana admin username"
  type        = string
  default     = "admin"
}

variable "grafana_admin_password" {
  description = "Grafana admin password"
  type        = string
  sensitive   = true
  default     = "admin"
}

variable "prometheus_retention_days" {
  description = "Number of days to retain Prometheus metrics"
  type        = number
  default     = 15
}

variable "enable_alertmanager" {
  description = "Enable Alertmanager deployment"
  type        = bool
  default     = false
}
