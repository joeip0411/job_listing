resource "aws_db_instance" "airflow-metastore" {
  allocated_storage                     = var.rds_allocated_storage
  apply_immediately                     = true
  availability_zone                     = var.rds_availability_zone
  backup_retention_period               = 1
  backup_window                         = var.rds_backup_window
  copy_tags_to_snapshot                 = true
  engine                                = "postgres"
  engine_version                        = "16.1"
  identifier                            = var.rds_name
  instance_class                        = var.rds_instance_class
  iops                                  = 0
  license_model                         = "postgresql-license"   
  maintenance_window                    = "fri:12:56-fri:13:26"
  # manage_master_user_password = true
  max_allocated_storage                 = 0
  monitoring_interval                   = 0
  multi_az                              = false
  network_type                          = "IPV4"
  option_group_name                     = "default:postgres-16"
  parameter_group_name                  = "default.postgres16"
  performance_insights_enabled          = false
  performance_insights_retention_period = 0
  port                                  = 5432
  publicly_accessible                   = false
  skip_final_snapshot                   = true
  storage_encrypted                     = true
  storage_throughput                    = 0
  storage_type                          = "gp2"
  username                              = var.rds_master_username
  vpc_security_group_ids                = [var.default_security_group]
}

output "POSTGRES_HOST" {
  value = aws_db_instance.airflow-metastore.address
}