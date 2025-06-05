output "report_address" {
    description = "Url to report image repository."
    value = aws_ecr_repository.report_pipeline_repo.repository_url
}

output "dashboard_address" {
    description = "Url to dashboard image repository."
    value = aws_ecr_repository.dash_pipeline_repo.repository_url
}