output "vercel_project_id" {
  description = "Vercel project ID — set as the VERCEL_PROJECT_ID secret for manual deploy workflows"
  value       = module.vercel.project_id
}
