output "zone_id" {
  description = "Cloudflare zone ID"
  value       = data.cloudflare_zone.this.id
}

output "frontend_record_id" {
  description = "Frontend DNS record ID"
  value       = cloudflare_record.frontend.id
}

output "api_record_id" {
  description = "API DNS record ID"
  value       = cloudflare_record.api.id
}

output "frontend_hostname" {
  description = "Frontend FQDN"
  value       = cloudflare_record.frontend.hostname
}

output "api_hostname" {
  description = "API FQDN"
  value       = cloudflare_record.api.hostname
}
