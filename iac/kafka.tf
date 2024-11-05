# resource "google_managed_kafka_cluster" "measurements_cluster" {
#   project = var.project-id
#   cluster_id = "measurments-cluster"
#   location   = "us-central1"
#   capacity_config {
#     vcpu_count   = 3
#     memory_bytes = 3221225472
#   }
#   gcp_config {
#     access_config {
#       network_configs {
#         subnet = "projects/${var.project-id}/regions/us-central1/subnetworks/default"
#       }
#     }
#   }
#   rebalance_config {
#     mode = "NO_REBALANCE"
#   }
#   labels = {
#     key = "value"
#   }

#   provider = google-beta
# }

# resource "google_managed_kafka_topic" "measurements_topic" {
#   project = var.project-id
#   topic_id           = "measurements"
#   cluster            = google_managed_kafka_cluster.measurements_cluster.cluster_id
#   location           = "us-central1"
#   partition_count    = 2
#   replication_factor = 3
#   configs = {
#     "cleanup.policy" = "compact"
#   }

#   provider = google-beta
# }

# data "google_project" "project" {
#   project_id = var.project-id
#   provider   = google-beta
# }
