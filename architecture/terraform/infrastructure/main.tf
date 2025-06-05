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
    repository_name = "c17-cattus-short-pipeline-ecr"
    image_tag = "latest"
}

data "aws_ecr_image" "long_pipe_image" {
    repository_name = "c17-cattus-long-pipeline-ecr"
    image_tag = "latest"
}

data "aws_vpc" "current-vpc" {
    id = "vpc-00b3f6b2893c390f2"
}

data "aws_iam_policy" "athena_full_access" {
    arn = "arn:aws:iam::aws:policy/AmazonAthenaFullAccess"
}

data "aws_iam_policy" "cloudwatch_full_access" {
    arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

data "aws_iam_policy" "ecs_full_access" {
    arn = "arn:aws:iam::aws:policy/AmazonECS_FullAccess"
}

data "aws_iam_policy" "ecr_full_access" {
    arn = "arn:aws:iam::aws:policy/AmazonElasticContainerRegistryPublicFullAccess"
}

data "aws_iam_policy" "ecs_service" {
    arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

data "aws_ecs_cluster" "c17-ecs-cluster" {
  cluster_name = "c17-ecs-cluster"
}

# S3 BUCKET

resource "aws_s3_bucket" "s3_bucket" {
    bucket = "c17-cattus-short-term-bucket"
    force_destroy = true
}

#  GLUE

data "aws_iam_policy" "glue_service_policy" {
    arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_glue_catalog_database" "data_catalog" {
    name = "c17-cattus-data"
}

resource "aws_iam_role" "glue_service_role" {
    name = "AWSGlueServiceRole-c17-cattus-service-role"
    assume_role_policy = jsonencode({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "glue.amazonaws.com"
                },
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {
                        "aws:SourceAccount": "129033205317"
                    }
                }
            }
        ]
    })
}

resource "aws_iam_role_policy_attachment" "glue_service_role_policy_attachment" {
    role = aws_iam_role.glue_service_role.name
    policy_arn = data.aws_iam_policy.glue_service_policy.arn
}

resource "aws_iam_policy" "glue_bucket_policy" {
    name = "AWSGlueServiceRole-c17-cattus-s3Policy"
    description = "Terraform managed policy for glue to interact with created bucket"
    policy = jsonencode({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject"
                ],
                "Resource": [
                    "arn:aws:s3:::${aws_s3_bucket.s3_bucket.bucket}/input/*"
                ],
                "Condition": {
                    "StringEquals": {
                        "aws:ResourceAccount": "129033205317"
                    }
                }
            }
        ]
    })
}

resource "aws_iam_role_policy_attachment" "glue_bucket_policy_attachment" {
    role = aws_iam_role.glue_service_role.name
    policy_arn = aws_iam_policy.glue_bucket_policy.arn
}

resource "aws_glue_crawler" "crawler" {
    database_name = aws_glue_catalog_database.data_catalog.name
    name = "c17-cattus-crawler"
    role = aws_iam_role.glue_service_role.arn
    schedule= "cron(10 0 * * ? *)"

    s3_target {
      path = "s3://${aws_s3_bucket.s3_bucket.bucket}/input/"
    }
}

resource "aws_glue_workflow" "workflow" {
    name = "c17-kyle-trucks-workflow"
}

resource "aws_glue_trigger" "start_crawler" {
    name = "c17-kyle-trucks-trigger"
    type = "ON_DEMAND"
    workflow_name = aws_glue_workflow.workflow.name

    actions {
        crawler_name = aws_glue_crawler.crawler.name
    }
}

# ECS

resource "aws_security_group" "ecs_sg" {
    name = "c17-cattus-ecs-sg"
    description = "Allows all outbound traffic from ECS."
    vpc_id = data.aws_vpc.current-vpc.id
}

resource "aws_vpc_security_group_egress_rule" "allow_all" {
  security_group_id = aws_security_group.ecs_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

resource "aws_vpc_security_group_ingress_rule" "allow_all_in" {
  security_group_id = aws_security_group.ecs_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

resource "aws_iam_role" "ecs_task_exec_role" {
    name = "c17-cattus-dashboard-exec"
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

resource "aws_iam_role_policy_attachment" "ecs_task_exec_athena" {
    role = aws_iam_role.ecs_task_exec_role.name
    policy_arn = data.aws_iam_policy.athena_full_access.arn
}

resource "aws_iam_role_policy_attachment" "ecs_task_exec_cloudwatch" {
    role = aws_iam_role.ecs_task_exec_role.name
    policy_arn = data.aws_iam_policy.cloudwatch_full_access.arn
}

resource "aws_iam_role_policy_attachment" "ecs_task_exec_ecr" {
    role = aws_iam_role.ecs_task_exec_role.name
    policy_arn = data.aws_iam_policy.ecr_full_access.arn
}

resource "aws_iam_role_policy_attachment" "ecs_task_exec_ecs" {
    role = aws_iam_role.ecs_task_exec_role.name
    policy_arn = data.aws_iam_policy.ecs_full_access.arn
}

resource "aws_iam_role_policy_attachment" "ecs_task_exec_ecs_role" {
    role = aws_iam_role.ecs_task_exec_role.name
    policy_arn = data.aws_iam_policy.ecs_service.arn
}

resource "aws_ecs_task_definition" "task" {
    depends_on = [ aws_iam_role_policy_attachment.ecs_task_exec_ecs_role ]
    family = "c17-cattus-dashboard-td" 
    memory = 2048
    cpu = 1024
    container_definitions = jsonencode([{
        name = "dashboard"
        image = "c17-cattus-dashboard-ecr:latest"
        cpu = 1024
        essential = true
        environment = [
            {
                "name": "S3_BUCKET",
                "value": aws_s3_bucket.s3_bucket.bucket
            },
            {
                "name": "AWS_REGION",
                "value": var.AWS_REGION
            },
            {
                "name": "GLUE_CATALOG_NAME",
                "value": aws_glue_catalog_database.data_catalog.name
            },
            {
                "name": "AWS_ACCESS_KEY_ID",
                "value": var.AWS_ACCESS_KEY
            },
            {
                "name": "AWS_SECRET_ACCESS_KEY",
                "value": var.AWS_SECRET_KEY
            }
        ]
    }])
    execution_role_arn = aws_iam_role.ecs_task_exec_role.arn
    task_role_arn = aws_iam_role.ecs_task_exec_role.arn
    runtime_platform {
      operating_system_family = "LINUX"
      cpu_architecture = "X86_64"
    }
    requires_compatibilities = ["FARGATE"]
    network_mode = "awsvpc"
}

resource "aws_ecs_service" "service" {
    depends_on = [ aws_iam_role_policy_attachment.ecs_task_exec_ecs_role ]
    name = "c17-cattus-dash-service"
    cluster = data.aws_ecs_cluster.c17-ecs-cluster.id
    task_definition = aws_ecs_task_definition.task.arn
    desired_count = 1
    launch_type = "FARGATE"
    force_delete = true
    network_configuration {
      subnets = [ var.SUBNET_1, var.SUBNET_2, var.SUBNET_3 ]
      security_groups = [ aws_security_group.ecs_sg.id ]
      assign_public_ip = true
    }
}

# LAMBDA

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

    function_name = "c17-cattus-short-pipeline-lambda"
    role          = aws_iam_role.lambda_role.arn

    package_type = "Image"
    image_uri = data.aws_ecr_image.short_pipe_image.image_uri

    environment {
        variables = {
            DB_HOST=var.DB_HOST
            DB_PORT=var.DB_PORT
            DB_USER=var.DB_USER
            DB_PASSWORD=var.DB_PASSWORD
            DB_NAME=var.DB_NAME
            DB_SCHEMA=var.DB_SCHEMA
            S3_BUCKET=aws_s3_bucket.s3_bucket.bucket
        }
    }
}

resource "aws_lambda_function" "long_pipeline_lambda" {
    depends_on = [ aws_iam_role_policy_attachment.lambda_role_attach ]
    timeout = 120
    memory_size = 1024

    function_name = "c17-cattus-long-pipeline-lambda"
    role          = aws_iam_role.lambda_role.arn

    package_type = "Image"
    image_uri = data.aws_ecr_image.long_pipe_image.image_uri

    environment {
        variables = {
            DB_HOST=var.DB_HOST
            DB_PORT=var.DB_PORT
            DB_USER=var.DB_USER
            DB_PASSWORD=var.DB_PASSWORD
            DB_NAME=var.DB_NAME
            DB_SCHEMA=var.DB_SCHEMA
            S3_BUCKET=aws_s3_bucket.s3_bucket.bucket
        }
    }
}

# Scheduler

resource "aws_iam_role" "scheduler_role" {
  name = "EventBridgeSchedulerRole-c17-cattus"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
        {
            Action = "sts:AssumeRole"
            Effect = "Allow"
            Principal = {
                Service = "scheduler.amazonaws.com"
            }
        }
    ]
  })
}

resource "aws_iam_role_policy" "eventbridge_invoke_policy" {
  name = "EventBridgeInvokePolicy"
  role = aws_iam_role.scheduler_role.id
  policy = jsonencode({
    "Version"   : "2012-10-17",
    "Statement" : [
        {
            "Sid"       : "AllowEventBridgeToInvokeLambda",
            "Action"    : ["lambda:InvokeFunction"],
            "Effect"    : "Allow",
            "Resource"  : [
              aws_lambda_function.short_pipeline_lambda.arn,
              aws_lambda_function.long_pipeline_lambda.arn,
              aws_lambda_function.report_lambda.arn
            ]
        }
    ] 
  })
}

resource "aws_scheduler_schedule" "report_schedule" {
  name       = "c17-cattus-report-schedule"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression =  "cron(* * * * ? *)"

  target {
    arn      = aws_lambda_function.report_lambda.arn
    role_arn = aws_iam_role.scheduler_role.arn
  }
}

resource "aws_scheduler_schedule" "short_pipe_schedule" {
  name       = "c17-cattus-short-pipeline-schedule"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression =  "cron(* * * * ? *)"

  target {
    arn      = aws_lambda_function.short_pipeline_lambda.arn
    role_arn = aws_iam_role.scheduler_role.arn
  }
}

resource "aws_scheduler_schedule" "long_pipe_schedule" {
  name       = "c17-cattus-long-pipeline-schedule"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression =  "cron(0 0 * * ? *)"

  target {
    arn      = aws_lambda_function.long_pipeline_lambda.arn
    role_arn = aws_iam_role.scheduler_role.arn
  }
}
