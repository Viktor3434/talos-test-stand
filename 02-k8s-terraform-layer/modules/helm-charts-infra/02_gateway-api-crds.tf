# 02-k8s-terraform-layer/modules/helm-charts-infra/gateway-api.tf

###
# Install CRDs
###
data "helm_template" "gateway_crds" {
  name      = "gateway-crd"
  chart     = "${path.module}/charts/gateway-helm-v1.8.1/charts/crds"
  namespace = var.gateway_api_namespace
  
  include_crds = true 
}

data "kubectl_file_documents" "split_gateway_crds" {
  content = data.helm_template.gateway_crds.manifest
}

resource "kubectl_manifest" "gateway_crds" {
  for_each  = data.kubectl_file_documents.split_gateway_crds.manifests
  yaml_body = each.value

  server_side_apply = true # CRD требуют server-side apply из-за размера OpenAPI схем
  force_conflicts   = true # При удалении стенда CRD удаляются автоматически

  depends_on = [data.kubectl_file_documents.split_gateway_crds]
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

  depends_on = [kubectl_manifest.gateway_crds]
}
