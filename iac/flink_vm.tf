resource "google_service_account" "flink-vm" {
  account_id   = "sa-flink-vm"
  display_name = "SA for Flink VM"
}

resource "google_project_iam_member" "storage-object-user" {
  project = var.project-id
  role    = "roles/storage.objectUser"
  member  = "serviceAccount:${google_service_account.flink-vm.email}"
}

# resource "google_compute_instance" "flink-vm" {
#   boot_disk {
#     auto_delete = true
#     device_name = "flink-vm"

#     initialize_params {
#       image = "projects/debian-cloud/global/images/debian-11-bullseye-v20241009"
#       size  = 10
#       type  = "pd-balanced"
#     }

#     mode = "READ_WRITE"
#   }

#   metadata_startup_script = file("${path.module}/vm_startup_script.sh")

#   can_ip_forward      = false
#   deletion_protection = false
#   enable_display      = false

#   labels = {
#     goog-ec-src = "vm_add-tf"
#   }

#   machine_type = "e2-medium"
#   name         = "flink-vm"

#   network_interface {
#     access_config {
#       network_tier = "PREMIUM"
#     }

#     queue_count = 0
#     stack_type  = "IPV4_ONLY"
#     subnetwork  = "projects/edc-igti-325912/regions/us-central1/subnetworks/default"
#   }

#   scheduling {
#     automatic_restart   = true
#     on_host_maintenance = "MIGRATE"
#     preemptible         = false
#     provisioning_model  = "STANDARD"
#   }

#   service_account {
#     email  = google_service_account.flink-vm.email
#     scopes = ["cloud-platform"]
#   }

#   shielded_instance_config {
#     enable_integrity_monitoring = true
#     enable_secure_boot          = false
#     enable_vtpm                 = true
#   }

#   tags = ["https-server", "lb-health-check", "flink-vm"]
#   zone = "us-central1-a"
# }