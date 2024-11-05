resource "google_compute_firewall" "rules" {
  project     = var.project-id
  name        = "flink-vm-ingress"
  network     = "default"
  description = "Creates firewall rule tfor port 8081"

  allow {
    protocol  = "tcp"
    ports     = ["8081"]
  }

  target_tags = ["flink-vm"]
  source_ranges = ["0.0.0.0/0"]
}