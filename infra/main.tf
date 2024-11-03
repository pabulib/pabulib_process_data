provider "google" {
  project = var.project_id
  region  = var.region
}

module "storage" {
  source        = "./modules/storage"
  bucket_name   = var.bucket_name
  location      = var.location
  storage_class = var.storage_class
}

module "service_account" {
  source        = "./modules/service_account"
  account_id    = var.account_id
  display_name  = "Storage Object Admin Service Account"
  bucket_name   = module.storage.bucket_name
}
