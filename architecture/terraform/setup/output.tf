output "report_ecr_uri" {
    description = "Url to report image repository."
    value = aws_ecr_repository.report_pipeline_repo.repository_url
}

output "dash_ecr_uri" {
    description = "Url to dashboard image repository."
    value = aws_ecr_repository.dash_pipeline_repo.repository_url
}

output "short_pipe_ecr_uri" {
    description = "Url to short term pipeline image repository."
    value = aws_ecr_repository.short_pipeline_repo.repository_url
}

output "long_pipe_ecr_uri" {
    description = "Url to historic pipeline image repository."
    value = aws_ecr_repository.long_pipeline_repo.repository_url
}