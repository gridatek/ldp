variable "namespace" {
  description = "Kubernetes namespace"
  type        = string
}

variable "worker_replicas" {
  description = "Number of Spark worker replicas"
  type        = number
  default     = 2
}

variable "master_nodeport_http" {
  description = "NodePort for Spark master HTTP"
  type        = number
  default     = 30707
}

variable "master_nodeport_cluster" {
  description = "NodePort for Spark master cluster communication"
  type        = number
  default     = 30077
}
