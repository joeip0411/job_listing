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