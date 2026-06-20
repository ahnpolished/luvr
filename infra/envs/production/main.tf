# --------------------------------------------------------------------
# Luvr Production Environment
# --------------------------------------------------------------------

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
    vercel = {
      source  = "vercel/vercel"
      version = "~> 1.0"
    }
    railway = {
      source  = "railwayapp/railway"
      version = ">= 0.2.0"
    }
  }
}

# --------------------------------------------------------------------
# Provider configs
# --------------------------------------------------------------------

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

provider "vercel" {
  api_token = var.vercel_api_token
}

provider "railway" {
  api_token = var.railway_api_token
}

# --------------------------------------------------------------------
# Variables
# --------------------------------------------------------------------

variable "cloudflare_api_token" {
  description = "Cloudflare API token"
  type        = string
  sensitive   = true
}

variable "vercel_api_token" {
  description = "Vercel API token"
  type        = string
  sensitive   = true
}

variable "railway_api_token" {
  description = "Railway API token"
  type        = string
  sensitive   = true
}

variable "zone_name" {
  description = "Cloudflare zone (root domain)"
  type        = string
}

variable "frontend_domain" {
  description = "Frontend domain"
  type        = string
}

variable "api_domain" {
  description = "API domain"
  type        = string
}

variable "github_repo" {
  description = "GitHub repo in owner/repo format"
  type        = string
}

variable "railway_project_name" {
  description = "Railway project name"
  type        = string
}

variable "vercel_project_name" {
  description = "Vercel project name"
  type        = string
}

variable "api_env_vars" {
  description = "API service env vars"
  type        = map(string)
  sensitive   = true
  default     = {}
}

variable "telegram_env_vars" {
  description = "Telegram worker env vars"
  type        = map(string)
  sensitive   = true
  default     = {}
}

variable "shared_env_vars" {
  description = "Shared env vars"
  type        = map(string)
  sensitive   = true
  default     = {}
}

# Placeholder CNAME target for the first apply.
# After Railway provisions the API service, grab the real CNAME target
# and update this value before the second apply.
variable "railway_cname_target" {
  description = "Railway CNAME target for the API domain (placeholder on first apply)"
  type        = string
  default     = "placeholder.railway.app"
}

# --------------------------------------------------------------------
# Cloudflare DNS
# --------------------------------------------------------------------

module "cloudflare" {
  source = "../../modules/cloudflare-dns"

  zone_name                = var.zone_name
  frontend_domain          = var.frontend_domain
  api_domain               = var.api_domain
  railway_cname_target     = var.railway_cname_target
  proxied                  = false # two-step: flip to true after cert provisioning
  ssl_mode                 = "full"
  enable_rate_limit        = true
  waf_rate_limit_threshold = 20 # stricter for production
}

# --------------------------------------------------------------------
# Railway (API + telegram-worker)
# --------------------------------------------------------------------

module "railway" {
  source = "../../modules/railway-service"

  project_name     = var.railway_project_name
  environment_name = "production"
  api_domain       = var.api_domain

  api_service_source = {
    repo   = var.github_repo
    branch = "main"
  }
  telegram_service_source = {
    repo   = var.github_repo
    branch = "main"
  }

  api_start_command            = null
  telegram_start_command       = null
  telegram_healthcheck_enabled = false

  shared_env_vars   = var.shared_env_vars
  api_env_vars      = var.api_env_vars
  telegram_env_vars = var.telegram_env_vars
}

# --------------------------------------------------------------------
# Vercel (frontend)
# --------------------------------------------------------------------

module "vercel" {
  source = "../../modules/vercel-project"

  project_name   = var.vercel_project_name
  git_repository = var.github_repo
  root_directory = "web"
  framework      = "vite"
  custom_domain  = var.frontend_domain
  api_base_url   = "https://${var.api_domain}"
}
