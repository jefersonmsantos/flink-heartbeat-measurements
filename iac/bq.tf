resource "google_bigquery_dataset" "measurements_dataset" {
  dataset_id                  = "measurements"
  description                 = "Dastaset to receive processed measurments data"
  location                    = "US"
}

resource "google_bigquery_table" "default" {
  dataset_id = google_bigquery_dataset.measurements_dataset.dataset_id
  table_id   = "heartbeat_average"

  schema = <<EOF
[
  {
    "name": "window_start",
    "type": "INTEGER",
    "mode": "NULLABLE"
  },
  {
    "name": "window_end",
    "type": "INTEGER",
    "mode": "NULLABLE"
  },
  {
    "name": "key",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "total",
    "type": "INTEGER",
    "mode": "NULLABLE"
  },
  {
    "name": "count",
    "type": "INTEGER",
    "mode": "NULLABLE"
  },
  {
    "name": "avg",
    "type": "FLOAT",
    "mode": "NULLABLE"
  }
]
EOF

  table_constraints {
    primary_key {
      columns = ["window_start","window_end","key"]
    }
  }
}