# provider
variable "aws_region" {
  type = string
}
variable "env" {
  type = string
}

# RDS (airflow metastore)
variable "rds_allocated_storage" {
  type        = number
}
variable "rds_availability_zone" {
  type        = string
}
variable "rds_backup_window" {
  type        = string
}
variable "rds_master_username" {
  type        = string
}
variable "rds_name" {
  type        = string
  description = "Name of RDS used for airflow metastore"
}
variable "rds_instance_class" {
  type        = string
  description = "Class instance type of RDS database"
}

# VPC
variable "default_vpc" {
  type        = string
}
variable "default_security_group" {
  type        = string
  description = "Default VPC security group id"
}

variable "default_subnet" {
  type = string
}
variable "ecs_task_security_group" {
  type = string
}
variable "my_home_ip" {
  type = string
}
variable "emr_master_security_group" {
  type = string
}
variable "emr_slave_security_group" {
  type = string
}

# ECR
variable "repo_name" {
  type = string
}

#S3
variable "datalake_storage_bucket"{
  type = string
}
variable "log_bucket" {
  type = string
}

#Glue
variable "aws_account_id" {
  type = string
}
variable "glue_database_name" {
  type = string
}

#ECS
variable "ecs_cluster_name" {
  type = string
}
variable "ecs_task_definition_family" {
  type = string
}

variable "ecs_service_name" {
  type = string
}