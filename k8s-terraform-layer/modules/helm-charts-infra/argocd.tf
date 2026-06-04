resource "helm_release" "argocd" {
  name             = "argocd"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  version          = "8.1.2"
  namespace        = var.argocd_namespace
  create_namespace = false

  values = [
    file("${path.module}/values/argocd-values.yaml")
  ]

  depends_on = [
    helm_release.envoy_gateway
  ]

  lifecycle {
    prevent_destroy = false
  }
}