resource "helm_release" "metrics_server" {
  name             = "metrics-server"
  repository       = "https://kubernetes-sigs.github.io/metrics-server/"
  chart            = "metrics-server"
  namespace        = "kube-system"
  create_namespace = false
  version          = "3.13.0" # Укажите актуальную версию

  values = [
    <<-EOT
      args:
        - --kubelet-insecure-tls
        - --kubelet-preferred-address-types=InternalIP
    EOT
  ]

  depends_on = [
    helm_release.gateway_api
  ]
}