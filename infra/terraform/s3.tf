resource "aws_s3_bucket" "datalake_storage_bucket" {
  bucket              = var.datalake_storage_bucket
  object_lock_enabled = false
}