resource "helm_release" "metrics_server" {
  name = "metrics-server"
  # repository       = "https://kubernetes-sigs.github.io/metrics-server/"
  chart            = "${path.module}/charts/metrics-server-3.13.0.tgz"
  namespace        = "kube-system"
  create_namespace = false
  # version          = "3.13.0"
  # timeout          = 600

  values = [
    <<-EOT
      args:
        - --kubelet-insecure-tls
        - --kubelet-preferred-address-types=InternalIP
    EOT
  ]
}
