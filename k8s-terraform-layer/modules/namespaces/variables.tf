variable "namespaces" {
  description = "List of namespaces to create"
  type        = list(string)
  default     = ["prometheus", "gateway-api", "argocd"]
}