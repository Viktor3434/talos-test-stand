resource "helm_release" "metallb" {
  name = "metallb"
  # repository       = "https://metallb.github.io/metallb"
  chart            = "${path.module}/charts/metallb-0.16.1.tgz"
  namespace        = var.metallb_namespace
  create_namespace = false
  # version          = "0.16.1"
  timeout = 240

  values = [file("${path.module}/values/metallb.yaml")]
}
