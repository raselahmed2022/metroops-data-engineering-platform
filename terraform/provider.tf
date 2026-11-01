provider "aws" {
  region = "eu-central-1"
}

data "aws_caller_identity" "current" {}