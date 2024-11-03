output "service_account_key" {
  description = "The private key for the service account in JSON format"
  value       = google_service_account_key.service_account_key.private_key
  sensitive   = true
}
