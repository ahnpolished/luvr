variable "project_name" {
  description = "Vercel project name"
  type        = string
}

variable "git_repository" {
  description = "GitHub repository in owner/repo format"
  type        = string
}

variable "root_directory" {
  description = "Root directory for the Vercel project (relative to repo root)"
  type        = string
  default     = "web"
}

variable "framework" {
  description = "Framework preset (e.g., vite, nextjs)"
  type        = string
  default     = "vite"
}

variable "custom_domain" {
  description = "Custom domain for the Vercel project"
  type        = string
}

variable "api_base_url" {
  description = "API base URL for the frontend to call (e.g., https://api.luvr.ahnpolished.com)"
  type        = string
}

variable "team_id" {
  description = "Vercel team ID (optional — omit for personal accounts)"
  type        = string
  default     = ""
}

variable "install_command" {
  description = "Vercel install command override"
  type        = string
  default     = "npm install"
}

variable "build_command" {
  description = "Vercel build command override"
  type        = string
  default     = "npm run build"
}

variable "output_directory" {
  description = "Vercel output directory"
  type        = string
  default     = "dist"
}
