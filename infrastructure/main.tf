resource "digitalocean_database_db" "database-example" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "postgres"
}

resource "digitalocean_database_cluster" "postgres" {
  name       = "postgres-cluster"
  engine     = "pg"
  version    = "12"
  size       = "db-s-1vcpu-1gb"
  region     = "nyc1"
  node_count = 1
}

resource "digitalocean_kubernetes_cluster" "k8s" {
  name   = "clsuter_main"
  region = "nyc1"
  # Grab the latest version slug from `doctl kubernetes options versions`
  version = "1.22.8-do.1"

  node_pool {
    name       = "worker-pool"
    size       = "s-2vcpu-2gb"
    node_count = 1

    taint {
      key    = "workloadKind"
      value  = "database"
      effect = "NoSchedule"
    }
  }
}


# Note: This doesn't work. The provider requires a cluster to exist to generate a token from.
# we can't define the cluster and the provider in the same spec. We would need to separate into different
# workspaces (ie different "states") and then import the cluster into the application workspace.
provider "kubernetes" {
  host  = digitalocean_kubernetes_cluster.k8s.endpoint
  token = digitalocean_kubernetes_cluster.k8s.kube_config[0].token
  cluster_ca_certificate = base64decode(
    digitalocean_kubernetes_cluster.k8s.kube_config[0].cluster_ca_certificate
  )
}

# There are plenty of other kubernetes resources missing: service, secrets, ingress controllers, etc.
# We're skipping for the sake of this exercise.
resource "kubernetes_deployment" "app" {
    metadata {
        name = "backend"
    }

    spec {
        replicas = 3

        selector {
        match_labels = {
            app = "backend"
        }
        }

        template {
        metadata {
            labels = {
            app = "example-app"
            }
        }

        spec {
            container {
            image = "backend:v0.1.0"
            name  = "backend"
            }
        }
        }
    }
}
