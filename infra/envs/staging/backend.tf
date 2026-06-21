# --------------------------------------------------------------------
# R2 backend (S3-compatible) for Terraform state
#
# The actual bucket, access key, and secret are provided via CI:
#   terraform init \
#     -backend-config="bucket=$TF_STATE_BUCKET" \
#     -backend-config="endpoint=$R2_ENDPOINT" \
#     -backend-config="access_key=$R2_ACCESS_KEY" \
#     -backend-config="secret_key=$R2_SECRET_KEY"
#
# The bucket and R2 credentials must be created manually as a one-time
# step outside of Terraform before the first apply.
# --------------------------------------------------------------------

terraform {
  backend "s3" {
    key = "staging/terraform.tfstate"
  }
}
