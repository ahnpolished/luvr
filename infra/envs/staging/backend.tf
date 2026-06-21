# --------------------------------------------------------------------
# GCS backend for Terraform state
#
# Auth via GOOGLE_BACKEND_CREDENTIALS env var in CI.
# Locally: gcloud auth application-default login
# --------------------------------------------------------------------

terraform {
  backend "gcs" {
    bucket = "luvr-tf-state"
    prefix = "staging"
  }
}
