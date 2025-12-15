# Spark Master StatefulSet
resource "kubernetes_stateful_set" "spark_master" {
  metadata {
    name      = "spark-master"
    namespace = var.namespace
    labels = {
      app       = "spark"
      component = "master"
    }
  }

  spec {
    service_name = "spark-master-headless"
    replicas     = 1

    selector {
      match_labels = {
        app       = "spark"
        component = "master"
      }
    }

    template {
      metadata {
        labels = {
          app       = "spark"
          component = "master"
        }
      }

      spec {
        container {
          name    = "spark-master"
          image   = "apache/spark:3.5.0"
          command = ["/opt/spark/bin/spark-class"]
          args    = ["org.apache.spark.deploy.master.Master"]

          env {
            name  = "SPARK_MODE"
            value = "master"
          }

          port {
            container_port = 8080
            name           = "http"
          }

          port {
            container_port = 7077
            name           = "cluster"
          }

          resources {
            requests = {
              memory = "1Gi"
              cpu    = "500m"
            }
          }
        }
      }
    }
  }
}

# Spark Master Service (NodePort for external access)
resource "kubernetes_service" "spark_master" {
  metadata {
    name      = "spark-master"
    namespace = var.namespace
  }

  spec {
    type = "NodePort"

    selector = {
      app       = "spark"
      component = "master"
    }

    port {
      name        = "http"
      port        = 8080
      target_port = 8080
      node_port   = var.master_nodeport_http
    }

    port {
      name        = "cluster"
      port        = 7077
      target_port = 7077
      node_port   = var.master_nodeport_cluster
    }
  }
}

# Spark Master Headless Service
resource "kubernetes_service" "spark_master_headless" {
  metadata {
    name      = "spark-master-headless"
    namespace = var.namespace
  }

  spec {
    cluster_ip = "None"

    selector = {
      app       = "spark"
      component = "master"
    }

    port {
      name        = "http"
      port        = 8080
      target_port = 8080
    }

    port {
      name        = "cluster"
      port        = 7077
      target_port = 7077
    }
  }
}

# Spark Worker Deployment
resource "kubernetes_deployment" "spark_worker" {
  metadata {
    name      = "spark-worker"
    namespace = var.namespace
    labels = {
      app       = "spark"
      component = "worker"
    }
  }

  spec {
    replicas = var.worker_replicas

    selector {
      match_labels = {
        app       = "spark"
        component = "worker"
      }
    }

    template {
      metadata {
        labels = {
          app       = "spark"
          component = "worker"
        }
      }

      spec {
        container {
          name    = "spark-worker"
          image   = "apache/spark:3.5.0"
          command = ["/opt/spark/bin/spark-class"]
          args    = ["org.apache.spark.deploy.worker.Worker", "spark://spark-master:7077"]

          env {
            name  = "SPARK_MODE"
            value = "worker"
          }

          env {
            name  = "SPARK_MASTER_URL"
            value = "spark://spark-master:7077"
          }

          env {
            name  = "SPARK_WORKER_MEMORY"
            value = "1G"
          }

          env {
            name  = "SPARK_WORKER_CORES"
            value = "1"
          }

          port {
            container_port = 8081
            name           = "http"
          }

          resources {
            requests = {
              memory = "1Gi"
              cpu    = "500m"
            }
          }
        }
      }
    }
  }
}
