output "pb_bucket_name" {
  description = "The name of the storage bucket"
  value       = module.pb_storage.bucket_name
}

output "web_bucket_name" {
  description = "The name of the storage bucket"
  value       = module.web_storage.bucket_name
}

output "pb_bucket_url" {
  description = "The URL of the bucket for all .pb files"
  value       = module.pb_storage.url
}

output "web_bucket_url" {
  description = "The URL of the bucket for production webpage .pb files"
  value       = module.web_storage.url
}
