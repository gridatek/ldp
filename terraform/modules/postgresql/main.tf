resource "kubernetes_stateful_set" "postgresql" {
  metadata {
    name      = "postgresql"
    namespace = var.namespace
    labels = {
      app = "postgresql"
    }
  }

  spec {
    service_name = "postgresql"
    replicas     = 1

    selector {
      match_labels = {
        app = "postgresql"
      }
    }

    template {
      metadata {
        labels = {
          app = "postgresql"
        }
      }

      spec {
        container {
          name  = "postgresql"
          image = "postgres:16"

          env {
            name  = "POSTGRES_USER"
            value = var.username
          }

          env {
            name  = "POSTGRES_PASSWORD"
            value = var.password
          }

          env {
            name  = "POSTGRES_DB"
            value = var.database
          }

          env {
            name  = "PGDATA"
            value = "/var/lib/postgresql/data/pgdata"
          }

          port {
            container_port = 5432
            name           = "postgresql"
          }

          volume_mount {
            name       = "data"
            mount_path = "/var/lib/postgresql/data"
          }

          resources {
            requests = {
              memory = "256Mi"
              cpu    = "250m"
            }
          }
        }
      }
    }

    volume_claim_template {
      metadata {
        name = "data"
      }

      spec {
        access_modes = ["ReadWriteOnce"]
        resources {
          requests = {
            storage = var.persistence_size
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "postgresql" {
  metadata {
    name      = "postgresql"
    namespace = var.namespace
  }

  spec {
    type = "NodePort"

    selector = {
      app = "postgresql"
    }

    port {
      port        = 5432
      target_port = 5432
      node_port   = var.nodeport
    }
  }
}

resource "kubernetes_service" "postgresql_headless" {
  metadata {
    name      = "postgresql-headless"
    namespace = var.namespace
  }

  spec {
    cluster_ip = "None"

    selector = {
      app = "postgresql"
    }

    port {
      port        = 5432
      target_port = 5432
    }
  }
}
