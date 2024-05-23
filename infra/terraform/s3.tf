resource "aws_s3_bucket" "datalake_storage_bucket" {
  bucket              = var.datalake_storage_bucket
  object_lock_enabled = false
}

resource "aws_s3_bucket" "log" {
  bucket              = var.log_bucket
  object_lock_enabled = false
}

output "GLUE_DATABASE_STORAGE_LOCATION" {
  value = aws_s3_bucket.datalake_storage_bucket.bucket
}

output "LOG_BUCKET" {
  value = aws_s3_bucket.log.bucket
}