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
my_home_ip = "49.199.152.109/32"
emr_master_security_group = "ElasticMapReduce-master"
emr_slave_security_group = "ElasticMapReduce-slave"