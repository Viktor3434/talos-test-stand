output "namespaces" {
  description = "Map of created namespaces"
  value       = { for k, v in kubernetes_namespace.this : k => v.metadata[0].name }
}

output "gateway_api_namespace" {
  description = "Name of gateway-api namespace"
  value       = kubernetes_namespace.this["envoy-gateway-system"].metadata[0].name
}

output "argocd_namespace" {
  description = "Name of argocd namespace"
  value       = kubernetes_namespace.this["argocd"].metadata[0].name
}