variable "namespaces" {
  description = "List of namespaces to create"
  type        = list(string)
  default     = ["prometheus", "envoy-gateway-system", "argocd"]
}