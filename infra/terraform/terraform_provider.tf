terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "joeip-data-engineering-job-listing-terraform"
    key = "terraform"
    region = "ap-southeast-2"
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

output "AWS_REGION" {
  value = var.aws_region
}