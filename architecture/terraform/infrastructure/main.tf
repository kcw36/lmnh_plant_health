provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_KEY
}

data "aws_ecr_image" "report_image" {
    repository_name = "c17-cattus-report-ecr"
    image_tag = "latest"
}

data "aws_ecr_image" "dash_image" {
    repository_name = "c17-cattus-dashboard-ecr"
    image_tag = "latest"
}

data "aws_ecr_image" "short_pipe_image" {
    repository_name = "c17-catus-short-pipeline-ecr"
    image_tag = "latest"
}

data "aws_ecr_image" "long_pipe_image" {
    repository_name = "c17-cattus-long-pipeline-ecr"
    image_tag = "latest"
}

resource "aws_security_group" "dash_ecs_sg" {
    name = "c17-cattus-dashboard-ecs-sg"
    description = "Allows all outbound traffic from ECS."
    vpc_id = data.aws_vpc.current-vpc.id
}

resource "aws_s3_bucket" "s3_bucket" {
    bucket = "c17-cattus-short-term-bucket"
    force_destroy = true
}

resource "aws_vpc_security_group_egress_rule" "allow_all" {
  security_group_id = aws_security_group.dash_ecs_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

resource "aws_vpc_security_group_ingress_rule" "allow_all_in" {
  security_group_id = aws_security_group.dash_ecs_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

resource "aws_iam_role" "ecs_task_exec_role" {
    name = "c17-cattus-dashboard-task-exec"
    assume_role_policy = jsonencode({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {
                    "Service": "ecs-tasks.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    })
}

resource "aws_iam_role" "lambda_role" {
    name = "c17-cattus-lambda-role"
    assume_role_policy = jsonencode({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    })
}

resource "aws_iam_policy" "lambda_policy" {
  name        = "c17-cattus-lambda-policy"
  description = "Allows Lambdas to run Athena queries, read Glue tables, access S3 results, and write logs"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "AthenaAccess",
        Effect = "Allow",
        Action = [
          "athena:StartQueryExecution",
          "athena:GetQueryExecution",
          "athena:GetQueryResults",
          "athena:GetWorkGroup"
        ],
        Resource = "*"
      },
      {
        Sid    = "GlueAccess",
        Effect = "Allow",
        Action = [
          "glue:GetDatabase",
          "glue:GetTable",
          "glue:DeleteTable",
          "glue:CreateTable",
          "glue:GetPartitions"
        ],
        Resource = "*"
      },
      {
        Sid    = "S3Access",
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
          "s3:DeleteObject",
          "s3:GetBucketLocation"
        ],
        Resource = [
          "arn:aws:s3:::${aws_s3_bucket.s3_bucket.bucket}",
          "arn:aws:s3:::${aws_s3_bucket.s3_bucket.bucket}/*"
        ]
      },
      {
        Sid    = "CloudWatchLogs",
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_role_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

resource "aws_lambda_function" "report_lambda" {
    depends_on = [ aws_iam_role_policy_attachment.lambda_role_attach ]
    timeout = 120
    memory_size = 1024

    function_name = "c17-cattus-report-lambda"
    role          = aws_iam_role.lambda_role.arn

    package_type = "Image"
    image_uri = data.aws_ecr_image.report_image.image_uri

    environment {
        variables = {
            
        }
    }
}

resource "aws_lambda_function" "short_pipeline_lambda" {
    depends_on = [ aws_iam_role_policy_attachment.lambda_role_attach ]
    timeout = 120
    memory_size = 1024

    function_name = "c17-cattus-report-lambda"
    role          = aws_iam_role.lambda_role.arn

    package_type = "Image"
    image_uri = data.aws_ecr_image.short_pipe_image.uri

    environment {
        variables = {
            
        }
    }
}

resource "aws_lambda_function" "long_pipeline_lambda" {
    depends_on = [ aws_iam_role_policy_attachment.lambda_role_attach ]
    timeout = 120
    memory_size = 1024

    function_name = "c17-cattus-report-lambda"
    role          = aws_iam_role.lambda_role.arn

    package_type = "Image"
    image_uri = data.aws_ecr_image.long_pipe_image.uri

    environment {
        variables = {
            
        }
    }
}

