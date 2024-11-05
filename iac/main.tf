terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.15.0"
    }
  }
}

provider "google" {
  project     = var.project-id
  credentials = "sa.json"
}


resource "google_storage_bucket" "tfstate" {
  name          = "heartbeat-tfstate"
  force_destroy = false
  location      = "US"
  storage_class = "STANDARD"
}