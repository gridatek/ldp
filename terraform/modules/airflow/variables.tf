variable "namespace" {
  description = "Kubernetes namespace"
  type        = string
}

variable "admin_username" {
  description = "Airflow admin username"
  type        = string
}

variable "admin_password" {
  description = "Airflow admin password"
  type        = string
  sensitive   = true
}

variable "postgresql_host" {
  description = "PostgreSQL host"
  type        = string
}

variable "postgresql_port" {
  description = "PostgreSQL port"
  type        = number
}

variable "postgresql_user" {
  description = "PostgreSQL user"
  type        = string
}

variable "postgresql_pass" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
}

variable "postgresql_db" {
  description = "PostgreSQL database"
  type        = string
}

variable "webserver_nodeport" {
  description = "NodePort for Airflow webserver"
  type        = number
  default     = 30080
}

variable "dags_persistence_size" {
  description = "Size of DAGs persistent volume"
  type        = string
  default     = "1Gi"
}

variable "logs_persistence_size" {
  description = "Size of logs persistent volume"
  type        = string
  default     = "5Gi"
}
