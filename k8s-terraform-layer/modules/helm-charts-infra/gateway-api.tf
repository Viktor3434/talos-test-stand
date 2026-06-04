# k8s-terraform-layer/modules/helm-charts-infra/gateway-api.tf

resource "helm_release" "envoy_gateway" {
  name             = "eg"
  repository       = "oci://docker.io/envoyproxy"
  chart            = "gateway-helm"
  version          = "v1.6.0"
  namespace        = var.gateway_api_namespace
  create_namespace = false
  timeout          = 600

  values = [
    file("${path.module}/values/gateway-api.yaml")
  ]
}