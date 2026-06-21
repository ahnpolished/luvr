# --------------------------------------------------------------------
# Luvr Production Environment
#
# Terraform manages Cloudflare DNS and Vercel.
# Railway is managed outside Terraform — see docs/deploy/DEPLOY.md.
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
# Provider configs
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
  description = "Cloudflare API token"
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

variable "vercel_project_name" {
  description = "Vercel project name"
  type        = string
}

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
  api_verify_txt_name  = "_railway-verify.api.luvr"
  api_verify_txt_value = "railway-verify=d71f62bfe3259b604ed41243b86fabf35f552dbc3d5e7e5a3919f1e091cc55b0"
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
