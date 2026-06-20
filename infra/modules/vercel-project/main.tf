# --------------------------------------------------------------------
# Vercel Project module for Luvr frontend
#
# Creates:
#   - Vercel project
#   - Custom domain with auto-SSL
#   - Environment variable (API base URL)
#
# NOTE: git_repository linking is configured via Vercel's GitHub App
# (installed on the repo), not via Terraform. The project_name must
# match the Vercel project created by the GitHub integration.
# --------------------------------------------------------------------

resource "vercel_project" "this" {
  name             = var.project_name
  framework        = var.framework
  root_directory   = var.root_directory
  team_id          = var.team_id != "" ? var.team_id : null
  install_command  = var.install_command
  build_command    = var.build_command
  output_directory = var.output_directory
}

# Custom domain
resource "vercel_project_domain" "this" {
  project_id = vercel_project.this.id
  domain     = var.custom_domain
  team_id    = var.team_id != "" ? var.team_id : null
}

# Environment variable
resource "vercel_project_environment_variable" "api_url" {
  project_id = vercel_project.this.id
  team_id    = var.team_id != "" ? var.team_id : null
  key        = "VITE_API_BASE_URL"
  value      = var.api_base_url
  target     = ["production", "preview", "development"]
}
