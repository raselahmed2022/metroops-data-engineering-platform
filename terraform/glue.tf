resource "aws_glue_catalog_database" "bronze" {
  name = "metroops_bronze"
}

resource "aws_glue_crawler" "bronze" {
  name          = "metroops-bronze-crawler"
  database_name = aws_glue_catalog_database.bronze.name

  role = "service-role/${aws_iam_role.glue_crawler.name}"

  configuration = jsonencode({
    CreatePartitionIndex = true
    Version              = 1.0
  })

  s3_target {
    path = "s3://${aws_s3_bucket.metroops_data.bucket}/bronze/"
  }
}