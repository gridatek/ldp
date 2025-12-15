# Create namespace for data platform
resource "kubernetes_namespace" "ldp" {
  metadata {
    name = var.namespace
    labels = {
      name = "local-data-platform"
    }
  }
}

# MinIO Module
module "minio" {
  source = "./modules/minio"

  namespace     = kubernetes_namespace.ldp.metadata[0].name
  root_user     = var.minio_root_user
  root_password = var.minio_root_password
}

# PostgreSQL Module
module "postgresql" {
  source = "./modules/postgresql"

  namespace = kubernetes_namespace.ldp.metadata[0].name
  username  = var.postgresql_username
  password  = var.postgresql_password
  database  = var.postgresql_database
}

# Airflow Module
module "airflow" {
  source = "./modules/airflow"

  namespace       = kubernetes_namespace.ldp.metadata[0].name
  admin_username  = var.airflow_admin_username
  admin_password  = var.airflow_admin_password
  postgresql_host = "postgresql"
  postgresql_port = 5432
  postgresql_user = var.postgresql_username
  postgresql_pass = var.postgresql_password
  postgresql_db   = var.postgresql_database

  depends_on = [module.postgresql]
}

# Spark Module
module "spark" {
  source = "./modules/spark"

  namespace       = kubernetes_namespace.ldp.metadata[0].name
  worker_replicas = var.spark_worker_replicas
}

# Jupyter Notebook for Spark development
resource "kubernetes_deployment" "jupyter" {
  depends_on = [module.spark, module.minio]

  metadata {
    name      = "jupyter"
    namespace = kubernetes_namespace.ldp.metadata[0].name
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "jupyter"
      }
    }

    template {
      metadata {
        labels = {
          app = "jupyter"
        }
      }

      spec {
        enable_service_links = false

        container {
          name  = "jupyter"
          image = "jupyter/pyspark-notebook:latest"

          port {
            container_port = 8888
          }

          env {
            name  = "JUPYTER_ENABLE_LAB"
            value = "yes"
          }

          env {
            name  = "SPARK_MASTER"
            value = "spark://spark-master:7077"
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

resource "kubernetes_service" "jupyter" {
  metadata {
    name      = "jupyter"
    namespace = kubernetes_namespace.ldp.metadata[0].name
  }

  spec {
    type = "NodePort"

    selector = {
      app = "jupyter"
    }

    port {
      port        = 8888
      target_port = 8888
      node_port   = 30888
    }
  }
}
