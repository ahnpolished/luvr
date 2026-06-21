# --------------------------------------------------------------------
# Cloudflare DNS module for Luvr
#
# Creates:
#   - CNAME records for frontend (→ Vercel) and API (→ Railway)
#   - Zone-level SSL/TLS override
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

resource "cloudflare_zone_settings_override" "this" {
  zone_id = data.cloudflare_zone.this.id

  settings {
    ssl = var.ssl_mode
    min_tls_version = "1.2"
    # Explicitly set read-only settings to avoid drift errors
    mirage             = "off"
    proxy_read_timeout = "100"
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
      mitigation_timeout  = 30
    }
  }
}
