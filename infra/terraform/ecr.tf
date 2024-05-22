resource "aws_ecr_repository" "airflow" {
  image_tag_mutability = "MUTABLE"
  name                 = var.repo_name
  encryption_configuration {
    encryption_type = "AES256"
  }
  image_scanning_configuration {
    scan_on_push = false
  }
}

output "aws_ecr_repository_url" {
  value = aws_ecr_repository.airflow.repository_url
}