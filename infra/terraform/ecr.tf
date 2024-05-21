resource "aws_ecr_repository" "airflow" {
  image_tag_mutability = "MUTABLE"
  name                 = "airflow"
  encryption_configuration {
    encryption_type = "AES256"
  }
  image_scanning_configuration {
    scan_on_push = false
  }
}

import {
  to = aws_ecr_repository.airflow
  id = "airflow"
}