# k8s-terraform-layer/modules/helm-charts-infra/gateway-api.tf

resource "helm_release" "gateway_api" {
  name             = "gateway-helm"
  # repository       = "oci://docker.io/envoyproxy" 
  chart            = "${path.module}/charts/gateway-helm"
  # version          = "v1.8.1"
  namespace        = var.gateway_api_namespace
  create_namespace = false
  timeout          = 600

  values = [
    file("${path.module}/values/gateway-api.yaml")
  ]
}