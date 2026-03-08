# Repository for your Python AI Agent
resource "aws_ecr_repository" "winsanity_etl" {
  name                 = "winsanity-etl"
  image_tag_mutability = "MUTABLE"
  force_delete         = true # Helpful for clean teardowns

  image_scanning_configuration {
    scan_on_push = true # Automatically checks your code for security bugs
  }
}

# Repository for your Next.js Web App
resource "aws_ecr_repository" "winsanity_web" {
  name                 = "winsanity-web"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }
}

# Output the URLs so you can use them in your terminal
output "etl_repo_url" {
  value = aws_ecr_repository.winsanity_etl.repository_url
}

output "web_repo_url" {
  value = aws_ecr_repository.winsanity_web.repository_url
}