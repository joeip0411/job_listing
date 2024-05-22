# # Security group
resource "aws_security_group" "ecs_task_airflow_job_listing" {
  description              = "Airflow job listing instance"
    name                   = var.ecs_task_security_group
    vpc_id                 = var.default_vpc
}

output "ecs_task_security_group_id" {
  value = aws_security_group.ecs_task_airflow_job_listing.id
}

resource "aws_vpc_security_group_ingress_rule" "ingress_from_airflow_metastore_to_ecs" {

  description                  = "Postgres DB"
  from_port                    = 0
  ip_protocol                  = "tcp"
  referenced_security_group_id = var.default_security_group
  security_group_id            = aws_security_group.ecs_task_airflow_job_listing.id
  to_port                      = 65535
}

resource "aws_vpc_security_group_ingress_rule" "ingress_from_home_to_ecs" {
  cidr_ipv4                    = var.my_home_ip
  description                  = "My home IP"
  from_port                    = 8080
  ip_protocol                  = "tcp"
  security_group_id            = aws_security_group.ecs_task_airflow_job_listing.id
  to_port                      = 8080
}

resource "aws_vpc_security_group_ingress_rule" "ingress_from_emr_to_ecs" {
  description                  = "EMR master node"
  from_port                    = 0
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.ElasticMapReduce_master.id
  security_group_id            = aws_security_group.ecs_task_airflow_job_listing.id
  to_port                      = 65535
}

resource "aws_vpc_security_group_egress_rule" "egress_from_ecs_to_emr" {
  description                  = "EMR master node"
  from_port                    = 10001
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.ElasticMapReduce_master.id
  security_group_id            = aws_security_group.ecs_task_airflow_job_listing.id
  to_port                      = 10001
}

resource "aws_vpc_security_group_egress_rule" "egress_from_ecs_to_internet" {
  cidr_ipv4                    = "0.0.0.0/0"
  ip_protocol                  = jsonencode(-1)
  security_group_id            = aws_security_group.ecs_task_airflow_job_listing.id
}

resource "aws_vpc_security_group_egress_rule" "egress_from_ecs_to_airflow_metastore" {
  description                  = "Postgres DB"
  from_port                    = 5432
  ip_protocol                  = "tcp"
  referenced_security_group_id = var.default_security_group
  security_group_id            = aws_security_group.ecs_task_airflow_job_listing.id
  to_port                      = 5432
}

resource "aws_security_group" "ElasticMapReduce_master" {
  description = "Master group for Elastic MapReduce created on 2024-04-16T21:27:14.386Z"
  name        = var.emr_master_security_group
  tags = {
    for-use-with-amazon-emr-managed-policies = "true"
  }
  tags_all = {
    for-use-with-amazon-emr-managed-policies = "true"
  }
  vpc_id = var.default_vpc
}

output "elastic_map_reduce_master_security_group_id" {
  value = aws_security_group.ElasticMapReduce_master.id
}


resource "aws_vpc_security_group_ingress_rule" "ingress_from_ecs_to_emr_master" {
  description                  = "ecs-task-airflow-job-listing"
  from_port                    = 10001
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.ecs_task_airflow_job_listing.id
  security_group_id            = aws_security_group.ElasticMapReduce_master.id
  to_port                      = 10001
}

resource "aws_vpc_security_group_ingress_rule" "ingress_from_emr_slave_to_emr_master_udp" { 
  from_port                    = 0
  ip_protocol                  = "udp"
  referenced_security_group_id = aws_security_group.ElasticMapReduce_slave.id
  security_group_id            = aws_security_group.ElasticMapReduce_master.id
  to_port                      = 65535
}

resource "aws_vpc_security_group_ingress_rule" "ingress_from_emr_slave_to_emr_master_icmp" {
  ip_protocol                  = "icmp"
  referenced_security_group_id = aws_security_group.ElasticMapReduce_slave.id
  security_group_id            = aws_security_group.ElasticMapReduce_master.id
}

resource "aws_vpc_security_group_ingress_rule" "ingress_from_emr_slave_to_emr_master_tcp" {
  from_port                    = 0
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.ElasticMapReduce_slave.id
  security_group_id            = aws_security_group.ElasticMapReduce_master.id
  to_port                      = 65535
}

resource "aws_vpc_security_group_ingress_rule" "ingress_from_firewall_regional_prod_only_to_emr_master_tcp" {
  from_port                    = 8443
  ip_protocol                  = "tcp"
  prefix_list_id               = "pl-05a7426c"
  security_group_id            = aws_security_group.ElasticMapReduce_master.id
  to_port                      = 8443
}

resource "aws_vpc_security_group_egress_rule" "egress_from_emr_master_to_internet" {
  cidr_ipv4                    = "0.0.0.0/0"
  ip_protocol                  = jsonencode(-1)
  security_group_id            = aws_security_group.ElasticMapReduce_master.id
}

resource "aws_security_group" "ElasticMapReduce_slave" {
  description = "Slave group for Elastic MapReduce created on 2024-04-16T21:27:14.386Z"
  name        = var.emr_slave_security_group
  tags = {
    for-use-with-amazon-emr-managed-policies = "true"
  }
  tags_all = {
    for-use-with-amazon-emr-managed-policies = "true"
  }
  vpc_id = var.default_vpc
}

output "elastic_map_reduce_slave_security_group_id" {
  value = aws_security_group.ElasticMapReduce_slave.id
}


resource "aws_vpc_security_group_ingress_rule" "ingress_from_emr_master_to_emr_slave_icmp" {
  ip_protocol                  = "icmp"
  referenced_security_group_id = aws_security_group.ElasticMapReduce_master.id
  security_group_id            = aws_security_group.ElasticMapReduce_slave.id
}

resource "aws_vpc_security_group_ingress_rule" "ingress_from_emr_master_to_emr_slave_tcp" {
  from_port                    = 0
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.ElasticMapReduce_master.id
  security_group_id            = aws_security_group.ElasticMapReduce_slave.id
  to_port                      = 65535
}

resource "aws_vpc_security_group_ingress_rule" "ingress_from_emr_master_to_emr_slave_udp" {
  from_port                    = 0
  ip_protocol                  = "udp"
  referenced_security_group_id = aws_security_group.ElasticMapReduce_master.id
  security_group_id            = aws_security_group.ElasticMapReduce_slave.id
  to_port                      = 65535
}

resource "aws_vpc_security_group_egress_rule" "egress_from_emr_slave_to_internet" {
  cidr_ipv4                    = "0.0.0.0/0"
  ip_protocol                  = jsonencode(-1)
  security_group_id            = aws_security_group.ElasticMapReduce_slave.id
}

output "default_subnet" {
  value = var.default_subnet
}