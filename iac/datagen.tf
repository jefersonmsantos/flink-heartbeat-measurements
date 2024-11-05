resource "google_secret_manager_secret" "secret-basic" {
  secret_id = "kafka-config"

  replication {
    auto {

    }
  }
}

# Creates docker artifact registry
resource "google_artifact_registry_repository" "docker-registry" {
  location      = var.region
  repository_id = "docker-registry"
  format        = "DOCKER"

  cleanup_policies {
    id     = "delete-old"
    action = "DELETE"
    condition {
      older_than = "432000s" # 5 days
      # Docs say we can specify eg. "5d", but when I tried it, I got an error saying:
      # "Field 'olderThan', Illegal duration format; duration must end with 's'"
    }
  }

  cleanup_policies {
    id     = "keep-recent"
    action = "KEEP"
    most_recent_versions {
      keep_count = 10
    }
  }
}

resource "google_service_account" "datagen-cloudrun" {
  account_id   = "sa-datagen-cloudrun"
  display_name = "SA for Datagen Cloudrun Job"
}

resource "google_secret_manager_secret_iam_member" "member" {
  project = google_secret_manager_secret.secret-basic.project
  secret_id = google_secret_manager_secret.secret-basic.secret_id
  role = "roles/secretmanager.secretAccessor"
  member = "serviceAccount:${google_service_account.datagen-cloudrun.email}"
}

resource "google_cloud_run_v2_job" "datagen-job" {
  name     = "datagen-job"
  location = "us-central1"

  template {
    template{
        service_account = google_service_account.datagen-cloudrun.email
        containers {
            image = "us-central1-docker.pkg.dev/edc-igti-325912/docker-registry/datagen:latest"
            resources {
                limits = {
                cpu    = "1"
                memory = "512Mi"
                }
            }
            
            env {
                name = "KAFKA_CREDENTIALS"
                value_source {
                secret_key_ref {
                    secret = google_secret_manager_secret.secret-basic.secret_id
                    version = "latest"
                }
                }
            }

        }
    }
  }
}
