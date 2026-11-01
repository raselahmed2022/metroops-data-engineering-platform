provider "aws" {
  region  = "eu-central-1"
  profile = "metroops-admin"
}

data "aws_caller_identity" "current" {}