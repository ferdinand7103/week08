terraform {
  required_version = ">= 1.7.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }

  # Remote state in Azure Storage, so every GitHub Actions run (and my laptop)
  # shares the same state file. The real values are passed in with
  # -backend-config during "terraform init" in the pipeline.
  backend "azurerm" {}
}

provider "azurerm" {
  features {}
}
