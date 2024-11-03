variable "bucket_name" {
  description = "Name of the storage bucket"
  type        = string
}

variable "location" {
  description = "Location for the storage bucket (multi-region 'EU' or single region)"
  type        = string
}

variable "storage_class" {
  description = "The storage class of the bucket"
  type        = string
}
