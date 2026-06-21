# --------------------------------------------------------------------
# R2 backend (S3-compatible) for Terraform state
#
# Configured per official Cloudflare guide:
#   https://developers.cloudflare.com/terraform/advanced-topics/remote-backend/
#
# Secrets are passed via -backend-config in CI (never committed).
# --------------------------------------------------------------------

terraform {
  backend "s3" {
    key = "production/terraform.tfstate"
  }
}
