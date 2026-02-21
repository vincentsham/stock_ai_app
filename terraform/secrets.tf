resource "aws_secretsmanager_secret" "db_password" {
  name = "winsanity/db_password"
}

resource "aws_secretsmanager_secret_version" "db_password_val" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = var.db_password # References the variable
}

resource "aws_secretsmanager_secret" "openai_key" {
  name = "winsanity/openai_key"
}

resource "aws_secretsmanager_secret_version" "openai_key_val" {
  secret_id     = aws_secretsmanager_secret.openai_key.id
  secret_string = var.openai_api_key # References the variable
}

resource "aws_secretsmanager_secret" "gemini_key" {
  name = "winsanity/gemini_key"
}

resource "aws_secretsmanager_secret_version" "gemini_key_val" {
  secret_id     = aws_secretsmanager_secret.gemini_key.id
  secret_string = var.gemini_api_key
}

resource "aws_secretsmanager_secret" "tavily_key" {
  name = "winsanity/tavily_key"
}

resource "aws_secretsmanager_secret_version" "tavily_key_val" {
  secret_id     = aws_secretsmanager_secret.tavily_key.id
  secret_string = var.tavily_api_key
}

resource "aws_secretsmanager_secret" "ninja_key" {
  name = "winsanity/ninja_key"
}

resource "aws_secretsmanager_secret_version" "ninja_key_val" {
  secret_id     = aws_secretsmanager_secret.ninja_key.id
  secret_string = var.ninja_api_key
}

resource "aws_secretsmanager_secret" "fmp_key" {
  name = "winsanity/fmp_key"
}

resource "aws_secretsmanager_secret_version" "fmp_key_val" {
  secret_id     = aws_secretsmanager_secret.fmp_key.id
  secret_string = var.fmp_api_key
}

resource "aws_secretsmanager_secret" "finnhub_key" {
  name = "winsanity/finnhub_key"
}

resource "aws_secretsmanager_secret_version" "finnhub_key_val" {
  secret_id     = aws_secretsmanager_secret.finnhub_key.id
  secret_string = var.finnhub_api_key
}

resource "aws_secretsmanager_secret" "db_connection_string" {
  name = "winsanity/db_connection_string"
}

resource "aws_secretsmanager_secret_version" "db_connection_string_val" {
  secret_id     = aws_secretsmanager_secret.db_connection_string.id
  secret_string = "postgresql://${var.db_username}:${var.db_password}@${split(":", aws_db_instance.winsanity_db.endpoint)[0]}:5432/${var.db_name}?sslmode=require"
}

