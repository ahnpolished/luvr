# --------------------------------------------------------------------
# Luvr Staging Environment
#
# Terraform manages Cloudflare DNS and Vercel.
# Railway is managed outside Terraform via railway.json + Railway's
# GitHub integration — see docs/deploy/DEPLOY.md.
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
  }
}

# --------------------------------------------------------------------
# Provider configs — credentials from env vars (never committed)
# --------------------------------------------------------------------

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

provider "vercel" {
  api_token = var.vercel_api_token
}

# --------------------------------------------------------------------
# Variables
# --------------------------------------------------------------------

variable "cloudflare_api_token" {
  description = "Cloudflare API token with DNS + Zone edit permissions"
  type        = string
  sensitive   = true
}

variable "vercel_api_token" {
  description = "Vercel API token"
  type        = string
  sensitive   = true
}

variable "zone_name" {
  description = "Cloudflare zone (root domain)"
  type        = string
}

variable "frontend_domain" {
  description = "Frontend domain for this environment"
  type        = string
}

variable "api_domain" {
  description = "API domain for this environment"
  type        = string
}

variable "github_repo" {
  description = "GitHub repo in owner/repo format"
  type        = string
}

variable "vercel_project_name" {
  description = "Vercel project name"
  type        = string
}

# Railway CNAME target — fill in after Railway provisions the API service.
# First apply: use any placeholder (e.g., "placeholder.railway.app")
# After Railway services are running: update to the real CNAME from Railway
# dashboard and re-apply.
variable "railway_cname_target" {
  description = "Railway CNAME target for the API domain"
  type        = string
  default     = "placeholder.railway.app"
}

# --------------------------------------------------------------------
# Cloudflare DNS
# --------------------------------------------------------------------

module "cloudflare" {
  source = "../../modules/cloudflare-dns"

  zone_name            = var.zone_name
  frontend_domain      = var.frontend_domain
  api_domain           = var.api_domain
  railway_cname_target = var.railway_cname_target
  api_verify_txt_name  = "_railway-verify.api-staging.luvr"
  api_verify_txt_value = "railway-verify=f56c46abdbe56eb4701c3b17c768a294ab0bd366a45a94356ca37404bdd07243"
  proxied              = false
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
