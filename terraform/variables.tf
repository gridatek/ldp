variable "namespace" {
  description = "Kubernetes namespace for the data platform"
  type        = string
  default     = "ldp"
}

variable "minio_root_user" {
  description = "MinIO root username"
  type        = string
  default     = "admin"
}

variable "minio_root_password" {
  description = "MinIO root password"
  type        = string
  default     = "minioadmin"
  sensitive   = true
}

variable "postgresql_username" {
  description = "PostgreSQL username"
  type        = string
  default     = "ldp"
}

variable "postgresql_password" {
  description = "PostgreSQL password"
  type        = string
  default     = "ldppassword"
  sensitive   = true
}

variable "postgresql_database" {
  description = "PostgreSQL database name"
  type        = string
  default     = "metastore"
}

variable "airflow_admin_username" {
  description = "Airflow admin username"
  type        = string
  default     = "admin"
}

variable "airflow_admin_password" {
  description = "Airflow admin password"
  type        = string
  default     = "admin"
  sensitive   = true
}

variable "spark_worker_replicas" {
  description = "Number of Spark worker replicas"
  type        = number
  default     = 2
}

# Monitoring variables
variable "enable_monitoring" {
  description = "Enable Prometheus and Grafana monitoring stack"
  type        = bool
  default     = true
}

variable "grafana_admin_username" {
  description = "Grafana admin username"
  type        = string
  default     = "admin"
}

variable "grafana_admin_password" {
  description = "Grafana admin password"
  type        = string
  default     = "admin"
  sensitive   = true
}
