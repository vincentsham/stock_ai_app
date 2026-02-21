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
        { name = "ENV",                    value = "production" },
        { name = "OPENAI_EMBEDDING_MODEL", value = "text-embedding-3-small" },
        { name = "OPENAI_LLM_MODEL",       value = "gpt-5-nano" },
        { name = "OPENAI_API_KEY",         value = var.openai_api_key },
        
        # Adding the specific key name your Python logs were looking for
        { name = "OPENAT_API_KEY",         value = var.openai_api_key },
        { name = "OPENAT_LLM_MODEL",       value = "gpt-5-nano" },

        { name = "GEMINI_API_KEY",         value = var.gemini_api_key },
        { name = "GEMINI_LLM_MODEL",       value = "models/gemini-2.5-flash-lite" },
        { name = "LLM_MODEL",              value = "chatgpt" },
        { name = "TAVILY_API_KEY",         value = var.tavily_api_key },
        { name = "NINJA_API_KEY",          value = var.ninja_api_key },
        { name = "FMP_API_KEY",            value = var.fmp_api_key },
        { name = "FINNHUB_API_KEY",        value = var.finnhub_api_key },
        
        # Database variables
        { name = "PGDATABASE",             value = var.db_name },
        { name = "PGUSER",                 value = var.db_username },
        { name = "PGPASSWORD",             value = var.db_password },
        { name = "PGHOST",                 value = split(":", aws_db_instance.winsanity_db.endpoint)[0] },
        { name = "PGPORT",                 value = "5432" },
        
        # Connection strings
        { name = "PGCONNECTION_TRANSACTION", value = "postgresql://${var.db_username}:${var.db_password}@${split(":", aws_db_instance.winsanity_db.endpoint)[0]}:5432/${var.db_name}?sslmode=require" },
        { name = "PGCONNECTION_SESSION",     value = "postgresql://${var.db_username}:${var.db_password}@${split(":", aws_db_instance.winsanity_db.endpoint)[0]}:5432/${var.db_name}?sslmode=require" }
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