variable "argocd_namespace" {
  description = "Namespace where ArgoCD will be installed"
  type        = string
}

variable "gateway_api_namespace" {
  description = "Namespace where Gateway-api will be installed"
  type        = string
}