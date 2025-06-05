provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_KEY
}

resource "aws_ecr_repository" "short_pipeline_repo" {
    name = "c17-cattus-short-pipeline-ecr"
    image_tag_mutability = "MUTABLE"
    image_scanning_configuration {
      scan_on_push = true
    }
    force_delete = true
}

resource "aws_ecr_repository" "long_pipeline_repo" {
    name = "c17-cattus-long-pipeline-ecr"
    image_tag_mutability = "MUTABLE"
    image_scanning_configuration {
      scan_on_push = true
    }
    force_delete = true
}

resource "aws_ecr_repository" "dash_pipeline_repo" {
    name = "c17-cattus-dashboard-ecr"
    image_tag_mutability = "MUTABLE"
    image_scanning_configuration {
      scan_on_push = true
    }
    force_delete = true
}

resource "aws_ecr_repository" "report_pipeline_repo" {
    name = "c17-cattus-report-ecr"
    image_tag_mutability = "MUTABLE"
    image_scanning_configuration {
      scan_on_push = true
    }
    force_delete = true
}