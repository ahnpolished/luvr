# Staging environment variables
#
# Values come from GitHub Actions Secrets — these are documented placeholders.
# Any secret values here will be overridden by CI.

zone_name            = "ahnpolished.com"
frontend_domain      = "staging.luvr.ahnpolished.com"
api_domain           = "api-staging.luvr.ahnpolished.com"
github_repo          = "ahnpolished/luvr"
railway_project_name = "luvr-staging"
vercel_project_name  = "luvr-staging"

# Secret values — populated from TF_VAR_ env vars in CI, never committed.
# cloudflare_api_token  = from TF_VAR_cloudflare_api_token
# vercel_api_token      = from TF_VAR_vercel_api_token
# railway_api_token     = from TF_VAR_railway_api_token

# Example env vars (real values come from GitHub Actions secrets)
api_env_vars = {
  PLATFORM = "server"
  PORT     = "8000"
}

telegram_env_vars = {
  PLATFORM      = "telegram"
  TELEGRAM_MODE = "polling"
}

shared_env_vars = {}
