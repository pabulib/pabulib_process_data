provider "google" {
  project = var.project_id
  region  = var.region
}

# Storage with all .pb files
module "pb_storage" {
  source        = "./modules/storage"
  bucket_name   = var.pb_bucket_name
  location      = var.location
  storage_class = var.storage_class
}


# Storage with prod .pb files
module "web_storage" {
  source        = "./modules/storage"
  bucket_name   = var.web_bucket_name
  location      = var.location
  storage_class = var.storage_class
}


# Admin Service Account with access to both buckets
module "service_account_admin" {
  source        = "./modules/service_account"
  account_id    = var.admin_account_id
  display_name  = "Storage Object Admin Service Account"
  bucket_names  = [module.pb_storage.bucket_name, module.web_storage.bucket_name]
  role          = "roles/storage.objectAdmin"
}

# Viewer Service Account with access only to the web bucket
module "service_account_viewer" {
  source        = "./modules/service_account"
  account_id    = var.viewer_account_id
  display_name  = "Storage Object Viewer Service Account"
  bucket_names  = [module.web_storage.bucket_name]  # Only the web bucket
  role          = "roles/storage.objectViewer"
}