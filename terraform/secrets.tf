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