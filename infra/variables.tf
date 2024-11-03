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

variable "bucket_name" {
  description = "Name of the storage bucket"
  type        = string
  default     = "pabulib_files"
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

variable "account_id" {
  description = "ID for the service account (unique within the project)"
  type        = string
  default     = "storage-object-admin-sa"
}
