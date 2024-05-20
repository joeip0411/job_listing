terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = var.storage_backend_bucket
    key = var.storage_backend_key
    region = var.aws_region
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      env = var.env
      project = "job_listing"
    }
  }
}
