output "bucket_name" {
  description = "The name of the storage bucket"
  value       = module.storage.bucket_name
}

output "bucket_url" {
  description = "The URL of the storage bucket"
  value       = module.storage.url
}


