# --------------------------------------------------------------------
# Cloudflare DNS module for Luvr
#
# Creates:
#   - CNAME records for frontend (→ Vercel) and API (→ Railway)
#   - Zone-level SSL/TLS settings
#   - Rate-limit WAF rule on /auth/alpha/*
#
# NOTE: DNS records must first be created with proxied = false so
# Railway/Vercel can verify the domain and issue their own TLS cert.
# Only flip to proxied = true afterward, then set ssl_mode = "strict".
# --------------------------------------------------------------------

data "cloudflare_zone" "this" {
  name = var.zone_name
}

# ---- DNS: frontend (→ Vercel) ----

resource "cloudflare_record" "frontend" {
  zone_id = data.cloudflare_zone.this.id
  name    = var.frontend_domain
  type    = "CNAME"
  value   = var.vercel_cname_target
  proxied = var.proxied
  comment = "Luvr frontend (Vercel)"
}

# ---- DNS: API (→ Railway) ----

resource "cloudflare_record" "api" {
  zone_id = data.cloudflare_zone.this.id
  name    = var.api_domain
  type    = "CNAME"
  value   = var.railway_cname_target
  proxied = var.proxied
  comment = "Luvr API (Railway)"
}

# ---- Zone SSL / TLS ----
# All settings must be explicitly listed — cloudflare_zone_settings_override
# reads the full zone settings payload and fails on read-only settings
# that are returned by the API but not declared in the block.

resource "cloudflare_zone_settings_override" "this" {
  zone_id = data.cloudflare_zone.this.id

  settings {
    ssl             = var.ssl_mode
    min_tls_version = "1.2"

    # Read-only settings (required to prevent drift errors on non-Enterprise plans)
    advanced_ddos               = "on"
    http2                       = "on"
    long_lived_grpc             = "off"
    mirage                      = "off"
    origin_error_page_pass_thru = "off"
    polish                      = "off"
    prefetch_preload            = "off"
    proxy_read_timeout          = "100"
    response_buffering          = "off"
    sort_query_string_for_cache = "off"
    true_client_ip_header       = "off"
    webp                        = "off"
  }
}

# ---- Rate-limit WAF rule ----

resource "cloudflare_ruleset" "rate_limit" {
  count = var.enable_rate_limit ? 1 : 0

  zone_id     = data.cloudflare_zone.this.id
  name        = "luvr-auth-rate-limit"
  description = "Rate-limit requests to /auth/alpha/*"
  kind        = "zone"
  phase       = "http_ratelimit"

  rules {
    action      = "block"
    description = "Rate-limit auth endpoints"
    expression  = "(http.request.uri.path contains \"/auth/alpha/\")"
    enabled     = true

    ratelimit {
      characteristics     = ["cf.colo.id", "ip.src"]
      period              = 10
      requests_per_period = var.waf_rate_limit_threshold
      mitigation_timeout  = 10
    }
  }
}
