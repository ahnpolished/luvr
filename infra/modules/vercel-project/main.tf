# --------------------------------------------------------------------
# Vercel Project module for Luvr frontend
#
# Creates:
#   - Vercel project linked to GitHub repo
#   - Custom domain with auto-SSL
#   - Environment variables (API base URL)
# --------------------------------------------------------------------

resource "vercel_project" "this" {
  name           = var.project_name
  framework      = var.framework
  root_directory = var.root_directory
  team_id        = var.team_id != "" ? var.team_id : null

  git_repository {
    type = "github"
    repo = var.git_repository
  }

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

# Environment variables
resource "vercel_project_environment_variables" "this" {
  project_id = vercel_project.this.id
  team_id    = var.team_id != "" ? var.team_id : null

  variables {
    key    = "VITE_API_BASE_URL"
    value  = var.api_base_url
    target = ["production", "preview", "development"]
    type   = "plain"
  }
}
