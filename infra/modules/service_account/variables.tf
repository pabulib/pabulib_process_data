variable "account_id" {
  description = "ID for the service account (unique within the project)"
  type        = string
}

variable "display_name" {
  description = "Display name for the service account"
  type        = string
}

variable "bucket_name" {
  description = "Name of the storage bucket to grant access to"
  type        = string
}
