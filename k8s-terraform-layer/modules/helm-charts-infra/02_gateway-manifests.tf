resource "kubectl_manifest" "gateway_class" {
  yaml_body = <<-YAML
    apiVersion: gateway.networking.k8s.io/v1
    kind: GatewayClass
    metadata:
      name: eg
    spec:
      controllerName: gateway.envoyproxy.io/gatewayclass-controller
  YAML

  depends_on = [
    kubectl_manifest.gateway_api_crds,
    helm_release.gateway_api
  ]
}

resource "kubectl_manifest" "gateway" {
  yaml_body = <<-YAML
    apiVersion: gateway.networking.k8s.io/v1
    kind: Gateway
    metadata:
      name: eg
      namespace: ${var.gateway_api_namespace}
    spec:
      gatewayClassName: eg
      listeners:
        - name: http
          protocol: HTTP
          port: 80
  YAML

  depends_on = [
    kubectl_manifest.gateway_api_crds,
    kubectl_manifest.gateway_class,
    helm_release.gateway_api
  ]
}