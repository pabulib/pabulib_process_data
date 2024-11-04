variable "project_id" {
  description = "The Google Cloud project ID"
  type        = string
  default     = "pabulib-uj"
}

variable "region" {
  description = "The region for Google resources"
  type        = string
  default     = "europe-central2"
}

variable "pb_bucket_name" {
  description = "Name of the bucket for all .pb files"
  type        = string
  default     = "pabulib_files"
}

variable "web_bucket_name" {
  description = "Name of the bucket for production webpage .pb files"
  type        = string
  default     = "pabulib_webpage_files"
}

variable "location" {
  description = "Location for the storage bucket (multi-region 'EU' or single region)"
  type        = string
  default     = "eu"
}

variable "storage_class" {
  description = "The storage class of the bucket"
  type        = string
  default     = "STANDARD"
}

variable "admin_account_id" {
  description = "ID for the admin service account with access to both buckets"
  type        = string
  default     = "storage-object-admin-sa"
}

variable "viewer_account_id" {
  description = "ID for the viewer service account with access to the web bucket only"
  type        = string
  default     = "storage-object-viewer-sa"
}