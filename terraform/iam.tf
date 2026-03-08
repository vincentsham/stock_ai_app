# 1. Execution Role (Allows AWS to pull image & push logs)
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "winsanity-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

# Attach the standard ECS execution policy
resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# IMPORTANT: Grant permission to read Secrets Manager
resource "aws_iam_role_policy" "secrets_policy" {
  name = "winsanity-secrets-policy"
  role = aws_iam_role.ecs_task_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = [
        aws_secretsmanager_secret.db_password.arn,
        aws_secretsmanager_secret.openai_key.arn,
        aws_secretsmanager_secret.gemini_key.arn,
        aws_secretsmanager_secret.tavily_key.arn,
        aws_secretsmanager_secret.ninja_key.arn,
        aws_secretsmanager_secret.fmp_key.arn,
        aws_secretsmanager_secret.finnhub_key.arn,
        aws_secretsmanager_secret.db_connection_string.arn,
        aws_secretsmanager_secret.supabase_connection_string.arn
      ]
    }]
  })
}

# 2. Task Role (Allows your Python code itself to interact with AWS)
resource "aws_iam_role" "ecs_task_role" {
  name = "winsanity-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}