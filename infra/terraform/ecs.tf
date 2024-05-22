resource "aws_ecs_cluster" "ecs_cluster" {
  name     = var.ecs_cluster_name
  configuration {
    execute_command_configuration {
      logging    = "DEFAULT"
    }
  }
  service_connect_defaults {
    namespace = aws_service_discovery_http_namespace.ecs_service_discovery_http_namespace.arn
  }
  setting {
    name  = "containerInsights"
    value = "disabled"
  }
}

resource "aws_service_discovery_http_namespace" "ecs_service_discovery_http_namespace" {
  name        = var.ecs_cluster_name
  tags = {
    AmazonECSManaged = "true"
  }
  tags_all = {
    AmazonECSManaged = "true"
  }
}

resource "aws_ecs_task_definition" "airflow_job_listing" {
  container_definitions = jsonencode([{
    command = ["scheduler"]
    cpu     = 1024
    essential        = true
    image            = format("%s:latest", aws_ecr_repository.airflow.repository_url)
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-create-group  = "true"
        awslogs-group         = format("/ecs/%s", var.ecs_task_definition_family)
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "ecs"
      }
    }
    name           = "airflow-scheduler"
    startTimeout   = 600
    stopTimeout    = 120
    }, {
    command = ["webserver"]
    cpu     = 1024
    essential        = true
    image            = format("%s:latest", aws_ecr_repository.airflow.repository_url)
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-create-group  = "true"
        awslogs-group         = format("/ecs/%s", var.ecs_task_definition_family)
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "ecs"
      }
    }
    name        = "airflow-webserver"
    portMappings = [{
      appProtocol   = "http"
      containerPort = 8080
      hostPort      = 8080
      name          = "airflow-webserver"
      protocol      = "tcp"
    }]
    startTimeout   = 600
    stopTimeout    = 120
  }])
  cpu                      = jsonencode(2048)
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  family                   = var.ecs_task_definition_family
  memory                   = jsonencode(4096)
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  track_latest             = false
  runtime_platform {
    cpu_architecture        = "X86_64"
    operating_system_family = "LINUX"
  }
}

output "ecs_task_definition_arn" {
  value = aws_ecs_task_definition.airflow_job_listing.arn
}

resource "aws_ecs_service" "airflow_job_listing" {
  cluster                            = aws_ecs_cluster.ecs_cluster.arn
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100
  desired_count                      = 0
  enable_ecs_managed_tags            = true
  enable_execute_command             = false
  health_check_grace_period_seconds  = 0
  name                               = var.ecs_service_name
  platform_version                   = "LATEST"
  propagate_tags                     = "NONE"
  scheduling_strategy                = "REPLICA"
  task_definition                    = format("%s:%s", aws_ecs_task_definition.airflow_job_listing.id, aws_ecs_task_definition.airflow_job_listing.revision)
  capacity_provider_strategy {
    base              = 0
    capacity_provider = "FARGATE_SPOT"
    weight            = 1
  }
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }
  deployment_controller {
    type = "ECS"
  }
  network_configuration {
    assign_public_ip = true
    security_groups  = [aws_security_group.ecs_task_airflow_job_listing.id]
    subnets          = [var.default_subnet]
  }
}
