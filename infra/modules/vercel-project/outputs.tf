output "project_id" {
  description = "Vercel project ID"
  value       = vercel_project.this.id
}

output "project_name" {
  description = "Vercel project name"
  value       = vercel_project.this.name
}

output "domain" {
  description = "Custom domain attached to the project"
  value       = vercel_project_domain.this.domain
}
