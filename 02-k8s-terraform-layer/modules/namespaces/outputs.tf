###
# Default NS
###
output "namespaces" {
  description = "Map of created namespaces"
  value       = { for k, v in kubernetes_namespace.default_ns : k => v.metadata[0].name }
}

output "gateway_api_namespace" {
  description = "Name of gateway-api namespace"
  value       = kubernetes_namespace.default_ns["envoy-gateway-system"].metadata[0].name
}

output "argocd_namespace" {
  description = "Name of argocd namespace"
  value       = kubernetes_namespace.default_ns["argocd"].metadata[0].name
}

###
# Privileged NS
###
output "metallb_namespace" {
  description = "Name of metallb namespace"
  value       = kubernetes_namespace_v1.privileged_ns["metallb"].metadata[0].name
}
