output "project_id" {
  description = "Railway project ID"
  value       = railway_project.this.id
}

output "api_service_id" {
  description = "API service ID"
  value       = railway_service.api.id
}

output "telegram_service_id" {
  description = "Telegram worker service ID"
  value       = railway_service.telegram.id
}

output "api_domain" {
  description = "Custom domain attached to the API service"
  value       = railway_service_domain.api.domain
}

output "railway_cname" {
  description = "Railway CNAME target for DNS"
  value       = railway_service_domain.api.cname_value
}
