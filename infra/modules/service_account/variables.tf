variable "account_id" {
  description = "ID for the service account (unique within the project)"
  type        = string
}

variable "display_name" {
  description = "Display name for the service account"
  type        = string
}

variable "bucket_names" {
  description = "List of storage buckets to grant access to"
  type        = list(string)
}

variable "role" {
  description = "IAM role to assign to the service account for the specified buckets"
  type        = string
}