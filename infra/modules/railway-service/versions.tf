terraform {
  required_version = ">= 1.5.0"

  required_providers {
    railway = {
      source  = "railwayapp/railway"
      version = ">= 0.2.0"
    }
  }
}
