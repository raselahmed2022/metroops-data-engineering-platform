resource "aws_s3_bucket" "metroops_data" {
  bucket = "metroops-data-rasal-2026"

  force_destroy = false
}