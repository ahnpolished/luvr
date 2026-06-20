# Production environment variables
#
# Values come from GitHub Actions Secrets — these are documented placeholders.

zone_name            = "ahnpolished.com"
frontend_domain      = "luvr.ahnpolished.com"
api_domain           = "api.luvr.ahnpolished.com"
github_repo          = "ahnpolished/luvr"
railway_project_name = "luvr"
vercel_project_name  = "luvr"

api_env_vars = {
  PLATFORM = "server"
  PORT     = "8000"
}

telegram_env_vars = {
  PLATFORM      = "telegram"
  TELEGRAM_MODE = "polling"
}

shared_env_vars = {}
