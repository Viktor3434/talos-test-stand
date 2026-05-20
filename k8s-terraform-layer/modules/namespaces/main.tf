resource "kubernetes_namespace" "prometheus" {
  metadata {
    name = "prometheus"
  }
}

resource "kubernetes_namespace" "gateway_api" {
  metadata {
    name = "gateway-api"
  }
}