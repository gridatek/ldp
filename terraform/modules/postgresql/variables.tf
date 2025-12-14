variable "namespace" {
  description = "Kubernetes namespace"
  type        = string
}

variable "username" {
  description = "PostgreSQL username"
  type        = string
}

variable "password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
}

variable "database" {
  description = "PostgreSQL database name"
  type        = string
}

variable "persistence_size" {
  description = "Size of persistent volume"
  type        = string
  default     = "8Gi"
}

variable "nodeport" {
  description = "NodePort for PostgreSQL"
  type        = number
  default     = 30432
}
