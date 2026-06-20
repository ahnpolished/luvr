# --------------------------------------------------------------------
# Railway Service module for Luvr
#
# Creates:
#   - One Railway project per environment
#   - Two services: `api` (FastAPI) and `telegram-worker` (polling bot)
#   - Custom domain on the API service
#   - Environment variables per service
#
# NOTE: Per-service start commands may not be supported by the
# community Railway provider. If not, use checked-in railway.json
# files instead — this module only manages project/service/env-var
# scaffolding in that case.
# --------------------------------------------------------------------

# Railway project
resource "railway_project" "this" {
  name = var.project_name
}

# -- API service (FastAPI) --

resource "railway_service" "api" {
  project_id     = railway_project.this.id
  name           = var.api_service_name
  environment_id = railway_project.this.default_environment_id

  # Source: GitHub repo link (optional — can also be set in Railway UI)
  dynamic "source" {
    for_each = var.api_service_source != null ? [var.api_service_source] : []
    content {
      repo   = source.value.repo
      branch = source.value.branch
    }
  }
}

# Custom domain for the API service
resource "railway_service_domain" "api" {
  service_id     = railway_service.api.id
  environment_id = railway_project.this.default_environment_id
  domain         = var.api_domain
}

# -- Telegram worker service --

resource "railway_service" "telegram" {
  project_id     = railway_project.this.id
  name           = var.telegram_service_name
  environment_id = railway_project.this.default_environment_id

  dynamic "source" {
    for_each = var.telegram_service_source != null ? [var.telegram_service_source] : []
    content {
      repo   = source.value.repo
      branch = source.value.branch
    }
  }
}

# -- Shared environment variables --

resource "railway_variable" "shared" {
  for_each       = var.shared_env_vars
  project_id     = railway_project.this.id
  environment_id = railway_project.this.default_environment_id
  name           = each.key
  value          = each.value
}

# -- API-specific environment variables --

resource "railway_variable" "api_env" {
  for_each       = var.api_env_vars
  project_id     = railway_project.this.id
  environment_id = railway_project.this.default_environment_id
  service_id     = railway_service.api.id
  name           = each.key
  value          = each.value
}

# -- Telegram-specific environment variables --

resource "railway_variable" "telegram_env" {
  for_each       = var.telegram_env_vars
  project_id     = railway_project.this.id
  environment_id = railway_project.this.default_environment_id
  service_id     = railway_service.telegram.id
  name           = each.key
  value          = each.value
}
