# 02-k8s-terraform-layer/modules/helm-charts-infra/gateway-api.tf

###
# Install CRDs
###
data "helm_template" "gateway_crd" {
  name      = "gateway-crd"
  chart     = "${path.module}/charts/gateway-helm-v1.8.1/charts/crds"
  namespace = var.gateway_api_namespace
}


resource "kubectl_manifest" "gateway_api_crds" {
  yaml_body = data.helm_template.gateway_crd.manifest

  server_side_apply = true # CRD требуют server-side apply из-за размера OpenAPI схем
  force_conflicts   = true # При удалении стенда CRD удаляются автоматически

  depends_on = [data.helm_template.gateway_crd]
}



###
# Install Envoy
###
resource "helm_release" "gateway_api" {
  name = "gateway-helm"
  # repository       = "oci://docker.io/envoyproxy" 
  chart = "${path.module}/charts/gateway-helm-v1.8.1"
  # version          = "v1.8.1"
  namespace        = var.gateway_api_namespace
  create_namespace = false
  timeout          = 600
  skip_crds        = true

  values = [file("${path.module}/values/gateway-api.yaml")]

  depends_on = [kubectl_manifest.gateway_api_crds]
}
