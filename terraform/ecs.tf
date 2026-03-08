# 1. The Cluster (The Logical Group)
resource "aws_ecs_cluster" "winsanity_cluster" {
  name = "winsanity-cluster"
}

# 2. The Task Definition (The Blueprint for your Agent)
resource "aws_ecs_task_definition" "etl_task" {
  family                   = "winsanity-etl-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024" # 1 vCPU
  memory                   = "2048" # 2 GB RAM
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

container_definitions = jsonencode([
    {
      name      = "winsanity-etl-agent"
      image     = "${aws_ecr_repository.winsanity_etl.repository_url}:latest"
      essential = true
      
      # All variables moved to environment for immediate execution
      environment = [
        { name = "APP_ENV",                    value = "aws" },
        { name = "ENV",                    value = "production" },
        { name = "OPENAI_EMBEDDING_MODEL", value = "text-embedding-3-small" },
        { name = "OPENAI_LLM_MODEL",       value = "gpt-5-nano" },
        { name = "GEMINI_LLM_MODEL",       value = "models/gemini-2.5-flash-lite" },
        { name = "LLM_MODEL",              value = "chatgpt" },
        
        # Database variables (Non-sensitive)
        { name = "PGDATABASE",             value = var.db_name },
        { name = "PGUSER",                 value = var.db_username },
        { name = "PGHOST",                 value = split(":", aws_db_instance.winsanity_db.endpoint)[0] },
        { name = "PGPORT",                 value = "5432" },
        { name = "PGSSLMODE",              value = "require" },
      ]

      secrets = [
        { name = "OPENAI_API_KEY",         valueFrom = aws_secretsmanager_secret.openai_key.arn },
        { name = "GEMINI_API_KEY",         valueFrom = aws_secretsmanager_secret.gemini_key.arn },
        { name = "TAVILY_API_KEY",         valueFrom = aws_secretsmanager_secret.tavily_key.arn },
        { name = "NINJA_API_KEY",          valueFrom = aws_secretsmanager_secret.ninja_key.arn },
        { name = "FMP_API_KEY",            valueFrom = aws_secretsmanager_secret.fmp_key.arn },
        { name = "FINNHUB_API_KEY",        valueFrom = aws_secretsmanager_secret.finnhub_key.arn },
        { name = "PGPASSWORD",             valueFrom = aws_secretsmanager_secret.db_password.arn },
        { name = "PGCONNECTION_TRANSACTION", valueFrom = aws_secretsmanager_secret.db_connection_string.arn },
        { name = "SUPABASE_TRANSACTION",      valueFrom = aws_secretsmanager_secret.supabase_connection_string.arn },
      ]

      # Log configuration set to camelCase for AWS API compliance
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/winsanity-etl"
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "etl"
        }
      }
    }
  ])
}

# 3. CloudWatch Log Group (To see your agent's output)
resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/winsanity-etl"
  retention_in_days = 7
}

# ============================================================
# WEB APP
# ============================================================

# 4. Task Definition for the Next.js Web App
resource "aws_ecs_task_definition" "web_task" {
  family                   = "winsanity-web-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"  # 0.5 vCPU
  memory                   = "1024" # 1 GB RAM
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "winsanity-web"
      image     = "${aws_ecr_repository.winsanity_web.repository_url}:latest"
      essential = true

      portMappings = [
        {
          containerPort = 3000
          hostPort      = 3000
          protocol      = "tcp"
        }
      ]

      # Non-sensitive environment variables
      environment = [
        { name = "APP_ENV",                      value = "aws" },
        { name = "NODE_ENV",                     value = "production" },
        { name = "NODE_TLS_REJECT_UNAUTHORIZED", value = "0" },
        { name = "PORT",                         value = "3000" },
        { name = "HOSTNAME",                     value = "0.0.0.0" },
      ]

      # Sensitive values pulled from Secrets Manager at runtime
      secrets = [
        { name = "PGCONNECTION_TRANSACTION", valueFrom = aws_secretsmanager_secret.db_connection_string.arn },
        { name = "FINNHUB_API_KEY",          valueFrom = aws_secretsmanager_secret.finnhub_key.arn },
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/winsanity-web"
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "web"
        }
      }
    }
  ])
}

# 5. CloudWatch Log Group for the Web App
resource "aws_cloudwatch_log_group" "web_logs" {
  name              = "/ecs/winsanity-web"
  retention_in_days = 7
}

# 6. ECS Service for the Web App (always-on, behind ALB)
resource "aws_ecs_service" "web_service" {
  name            = "winsanity-web-service"
  cluster         = aws_ecs_cluster.winsanity_cluster.id
  task_definition = aws_ecs_task_definition.web_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.public_subnets
    security_groups  = [aws_security_group.web_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.web_tg.arn
    container_name   = "winsanity-web"
    container_port   = 3000
  }

  # Wait for the listener to exist before creating the service
  depends_on = [aws_lb_listener.web_http]
}