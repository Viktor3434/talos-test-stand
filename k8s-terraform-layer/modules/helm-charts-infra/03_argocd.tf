resource "helm_release" "argocd" {
  name = "argocd"
  # repository       = "https://argoproj.github.io/argo-helm"
  chart = "${path.module}/charts/argo-cd-9.5.20.tgz"
  # version          = "9.5.20"
  namespace        = var.argocd_namespace
  create_namespace = false

  values = [
    file("${path.module}/values/argocd.yaml")
  ]

  depends_on = [
    helm_release.gateway_api,
    kubectl_manifest.gateway_api_crds,
    kubectl_manifest.gateway_class,
    kubectl_manifest.gateway,
  ]

  lifecycle {
    prevent_destroy = false
  }
}
