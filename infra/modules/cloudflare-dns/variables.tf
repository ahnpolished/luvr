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

variable "proxied" {
  description = "Whether Cloudflare proxy (orange cloud) is enabled for DNS records"
  type        = bool
  default     = false
}

variable "api_verify_txt_name" {
  description = "DNS name for the Railway domain verification TXT record (e.g., _railway-verify.api)"
  type        = string
  default     = ""
}

variable "api_verify_txt_value" {
  description = "TXT value for the Railway domain verification record"
  type        = string
  default     = ""
}
