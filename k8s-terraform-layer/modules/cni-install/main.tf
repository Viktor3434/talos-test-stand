resource "helm_release" "cilium" {
  name             = "cilium"
  repository       = "https://helm.cilium.io/"
  chart            = "cilium"
  version          = "1.16.5"
  namespace        = "kube-system"
  create_namespace = false

  values = [
    file("${path.module}/values/cilium-values.yaml")
  ]
}