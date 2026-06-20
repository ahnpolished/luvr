variable "project_name" {
  description = "Railway project name (e.g., luvr-staging)"
  type        = string
}

variable "environment_name" {
  description = "Railway environment name (e.g., production)"
  type        = string
  default     = "production"
}

variable "api_service_name" {
  description = "Name for the FastAPI service"
  type        = string
  default     = "api"
}

variable "telegram_service_name" {
  description = "Name for the Telegram bot worker service"
  type        = string
  default     = "telegram-worker"
}

variable "api_domain" {
  description = "Custom domain for the API service (e.g., api.luvr.ahnpolished.com)"
  type        = string
}

variable "api_service_source" {
  description = "Source config for the API service: repo and build settings"
  type = object({
    repo   = string
    branch = optional(string, "main")
  })
  default = null
}

variable "telegram_service_source" {
  description = "Source config for the Telegram worker service"
  type = object({
    repo   = string
    branch = optional(string, "main")
  })
  default = null
}

variable "api_env_vars" {
  description = "Environment variables for the API service"
  type        = map(string)
  default     = {}
  sensitive   = true
}

variable "telegram_env_vars" {
  description = "Environment variables for the Telegram worker service"
  type        = map(string)
  default     = {}
  sensitive   = true
}

variable "shared_env_vars" {
  description = "Environment variables shared by both services"
  type        = map(string)
  default     = {}
  sensitive   = true
}

# --- Start commands ---
# NOTE: The community Railway provider may not support per-service start
# commands. If so, these are configured in checked-in railway.json files
# instead, and only project/service/env-var/domain scaffolding is managed
# by Terraform.

variable "api_start_command" {
  description = "API service start command (null → use railway.json)"
  type        = string
  default     = null
}

variable "telegram_start_command" {
  description = "Telegram worker start command (null → use railway.json)"
  type        = string
  default     = null
}

variable "api_healthcheck_path" {
  description = "Health check path for the API service"
  type        = string
  default     = "/health"
}

variable "telegram_healthcheck_enabled" {
  description = "Whether to enable health check for telegram-worker (no HTTP port)"
  type        = bool
  default     = false
}
