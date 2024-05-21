# provider
aws_region="ap-southeast-2"
env = "prod"

# RDS (airflow metastore)
rds_allocated_storage = 20
rds_availability_zone = "ap-southeast-2a"
rds_backup_window = "17:08-17:38"
rds_master_username = "postgres"
rds_name = "airflow-metastore"
rds_instance_class = "db.t3.micro"

# VPC
default_security_group = "sg-03cf555952fc36384"
default_vpc = "vpc-08145d8c589b57547"
ecs_task_security_group = "ecs-task-airflow-job-listing"
emr_master_security_group = "ElasticMapReduce-master"
emr_slave_security_group = "ElasticMapReduce-slave"
my_home_ip = "49.199.152.109/32"

# ECR
repo_name = "airflow"

# S3
datalake_storage_bucket = "joeip-data-engineering-iceberg-test"

# Glue
aws_account_id = "654654412098"
glue_database_name = "job"