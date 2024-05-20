# provider
variable "storage_backend_bucket" {
  type = string
}
variable "storage_backend_key" {
  type = string
}
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