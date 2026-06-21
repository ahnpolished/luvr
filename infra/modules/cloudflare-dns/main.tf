# --------------------------------------------------------------------
# Cloudflare DNS module for Luvr
#
# Creates:
#   - CNAME records for frontend (→ Vercel) and API (→ Railway)
#
# NOTE: DNS records must first be created with proxied = false so
# Railway/Vercel can verify the domain and issue their own TLS cert.
# Only flip to proxied = true afterward, then set ssl_mode = "strict".
#
# Zone SSL/TLS settings (ssl_mode, min_tls_version) are configured
# manually in the Cloudflare dashboard — cloudflare_zone_settings_override
# is incompatible with non-Enterprise plans due to read-only setting drift.
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

# ---- DNS: Railway domain verification TXT ----

resource "cloudflare_record" "api_verify_txt" {
  zone_id = data.cloudflare_zone.this.id
  name    = var.api_verify_txt_name
  type    = "TXT"
  value   = var.api_verify_txt_value
  comment = "Railway custom domain verification"
}
