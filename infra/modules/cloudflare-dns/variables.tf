variable "zone_name" {
  description = "Cloudflare zone name (e.g., ahnpolished.com)"
  type        = string
}

variable "frontend_domain" {
  description = "Fully qualified frontend domain (e.g., luvr.ahnpolished.com)"
  type        = string
}

variable "api_domain" {
  description = "Fully qualified API domain (e.g., api.luvr.ahnpolished.com)"
  type        = string
}

variable "vercel_cname_target" {
  description = "Vercel CNAME target for the frontend domain"
  type        = string
  default     = "cname.vercel-dns.com"
}

variable "railway_cname_target" {
  description = "Railway CNAME target for the API domain"
  type        = string
}

variable "enable_rate_limit" {
  description = "Whether to create a rate-limit WAF rule on /auth/alpha/*"
  type        = bool
  default     = true
}

variable "waf_rate_limit_threshold" {
  description = "WAF rate-limit requests per 10 seconds"
  type        = number
  default     = 30
}

variable "ssl_mode" {
  description = "Cloudflare SSL/TLS mode (off, flexible, full, strict)"
  type        = string
  default     = "full"

  validation {
    condition     = contains(["off", "flexible", "full", "strict"], var.ssl_mode)
    error_message = "ssl_mode must be one of: off, flexible, full, strict."
  }
}

variable "proxied" {
  description = "Whether Cloudflare proxy (orange cloud) is enabled for DNS records"
  type        = bool
  default     = false
}
