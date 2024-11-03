resource "google_service_account" "service_account" {
  account_id   = var.account_id
  display_name = var.display_name
}

resource "google_storage_bucket_iam_member" "bucket_access" {
  bucket = var.bucket_name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.service_account.email}"
}

# Create a service account key
resource "google_service_account_key" "service_account_key" {
  service_account_id = google_service_account.service_account.name
  key_algorithm      = "KEY_ALG_RSA_2048"
  private_key_type   = "TYPE_GOOGLE_CREDENTIALS_FILE"
}

# Save the key to a JSON file in a secure location
resource "local_file" "service_account_key_file" {
  content  = "${base64decode(google_service_account_key.service_account_key.private_key)}"
  filename = "${path.root}/service_account_key.json"  # Adjust this path as needed
}
