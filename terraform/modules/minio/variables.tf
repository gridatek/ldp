variable "namespace" {
  description = "Kubernetes namespace"
  type        = string
}

variable "root_user" {
  description = "MinIO root username"
  type        = string
}

variable "root_password" {
  description = "MinIO root password"
  type        = string
  sensitive   = true
}

variable "persistence_size" {
  description = "Size of persistent volume"
  type        = string
  default     = "10Gi"
}

variable "api_nodeport" {
  description = "NodePort for MinIO API"
  type        = number
  default     = 30900
}

variable "console_nodeport" {
  description = "NodePort for MinIO Console"
  type        = number
  default     = 30901
}
