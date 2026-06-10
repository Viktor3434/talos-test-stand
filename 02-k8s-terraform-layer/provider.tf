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
    kubectl = {
      source  = "alekc/kubectl"
      version = "~> 2.4.1"
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

provider "kubectl" {
  config_path = "~/.kube/config"
}