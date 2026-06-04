output "prometheus_namespace" {
  description = "Name of Prometheus namespace"
  value       = kubernetes_namespace.prometheus.metadata[0].name
}

output "gateway_api_namespace" {
  description = "Name of Gateway API namespace"
  value       = kubernetes_namespace.gateway_api.metadata[0].name
}

output "argocd_namespace" {
  description = "Name of ArgoCD namespace"
  value       = kubernetes_namespace.argocd.metadata[0].name
}