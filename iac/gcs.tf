resource "google_storage_bucket" "flink-files" {
  name          = "heartbeat-flink-files"
  force_destroy = false
  location      = "US"
  storage_class = "STANDARD"
}

resource "google_storage_bucket_object" "docker-compose" {
  name   = "docker-compose.yml"
  source = "../processing/docker-compose.yml"
  bucket = google_storage_bucket.flink-files.name
}

resource "google_storage_bucket_object" "sa-json" {
  name   = "gcp_auth/bqsa.json"
  source = "../processing/gcp_auth/bqsa.json"
  bucket = google_storage_bucket.flink-files.name
}
