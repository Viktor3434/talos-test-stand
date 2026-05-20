terraform {
  required_version = ">=1.15.3"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.30"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 3.1.1"
    }
    talos = {
      source  = "siderolabs/talos"
      version = "~> 0.11"
    }
  }
}


provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = "admin@talos-cluster"
}

provider "helm" {
  kubernetes = {
    config_path = "~/.kube/config"
  }
}