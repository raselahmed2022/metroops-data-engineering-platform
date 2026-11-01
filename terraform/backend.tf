terraform {
  backend "s3" {
    bucket       = "metroops-tfstate-rasal-2026"
    key          = "metroops/terraform.tfstate"
    region       = "eu-central-1"
    encrypt      = true
    use_lockfile = true
  }
}