terraform {
  backend "s3" {
    bucket         = "winsanity-terraform-state-3329b817"
    key            = "state/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "winsanity-state-lock"
    encrypt        = true
  }
}