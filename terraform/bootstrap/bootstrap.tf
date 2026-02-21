provider "aws" {
  region = "us-east-1" # Ensure this matches your intended region
}

# 1. The S3 Bucket for State Storage
resource "aws_s3_bucket" "terraform_state" {
  bucket = "winsanity-terraform-state-${random_id.suffix.hex}" # Must be globally unique
  
  # Prevent accidental deletion of this bucket
  lifecycle {
    prevent_destroy = true
  }
}

# Enable versioning so you can see every change to your state
resource "aws_s3_bucket_versioning" "enabled" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

# 2. The DynamoDB Table for State Locking
resource "aws_s3_bucket_server_side_encryption_configuration" "default" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "winsanity-state-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

resource "random_id" "suffix" {
  byte_length = 4
}

output "s3_bucket_name" {
  value = aws_s3_bucket.terraform_state.bucket
}