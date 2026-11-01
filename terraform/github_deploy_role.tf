resource "aws_iam_role" "github_deploy" {
  name = "MetroOpsGitHubDeployRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        }

        Action = "sts:AssumeRoleWithWebIdentity"

        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
            "token.actions.githubusercontent.com:sub" = "repo:raselahmed2022@109651577/metroops-data-engineering-platform@1442258790:environment:production"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "github_deploy" {
  name = "MetroOpsTerraformDeploymentPolicy"
  role = aws_iam_role.github_deploy.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      # Terraform remote state
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = "arn:aws:s3:::metroops-tfstate-rasal-2026"
      },

      {
        Effect = "Allow"

        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]

        Resource = "arn:aws:s3:::metroops-tfstate-rasal-2026/metroops/terraform.tfstate"
      },

      {
        Effect = "Allow"

        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]

        Resource = "arn:aws:s3:::metroops-tfstate-rasal-2026/metroops/terraform.tfstate.tflock"
      },

      # MetroOps S3 infrastructure
      {
        Effect = "Allow"

        Action = [
          "s3:Get*",
          "s3:List*",
          "s3:PutBucket*",
          "s3:DeleteBucketTagging"
        ]

        Resource = aws_s3_bucket.metroops_data.arn
      },

      # Glue infrastructure
      {
        Effect = "Allow"

        Action = [
          "glue:GetDatabase",
          "glue:GetDatabases",
          "glue:CreateDatabase",
          "glue:UpdateDatabase",
          "glue:DeleteDatabase",
          "glue:GetCrawler",
          "glue:GetCrawlers",
          "glue:CreateCrawler",
          "glue:UpdateCrawler",
          "glue:DeleteCrawler"
        ]

        Resource = "*"
      },

      # Manage the Glue execution role
      {
        Effect = "Allow"

        Action = [
          "iam:GetRole",
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:UpdateRole",
          "iam:UpdateRoleDescription",
          "iam:UpdateAssumeRolePolicy",
          "iam:ListRolePolicies",
          "iam:GetRolePolicy",
          "iam:PutRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:ListAttachedRolePolicies",
          "iam:TagRole",
          "iam:UntagRole"
        ]

        Resource = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/service-role/AWSGlueServiceRole-MetroOpsBronzeCrawler"
      },

      {
        Effect   = "Allow"
        Action   = ["iam:PassRole"]
        Resource = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/service-role/AWSGlueServiceRole-MetroOpsBronzeCrawler"
      },

      # GitHub deployment role: READ ONLY
      {
        Effect = "Allow"

        Action = [
          "iam:GetRole",
          "iam:ListRolePolicies",
          "iam:GetRolePolicy",
          "iam:ListAttachedRolePolicies"
        ]

        Resource = aws_iam_role.github_deploy.arn
      },

      # GitHub OIDC provider: READ ONLY
      {
        Effect   = "Allow"
        Action   = ["iam:GetOpenIDConnectProvider"]
        Resource = aws_iam_openid_connect_provider.github.arn
      },

      {
        Effect   = "Allow"
        Action   = ["iam:ListOpenIDConnectProviders"]
        Resource = "*"
      }
    ]
  })
}