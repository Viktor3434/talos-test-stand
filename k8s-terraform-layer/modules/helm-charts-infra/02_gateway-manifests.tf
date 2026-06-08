resource "kubectl_manifest" "envoy_proxy" {
  yaml_body = <<-YAML
    apiVersion: gateway.envoyproxy.io/v1alpha1
    kind: EnvoyProxy
    metadata:
      name: custom-proxy-config
      namespace: ${var.gateway_api_namespace}
    spec:
      provider:
        type: Kubernetes
        kubernetes:
          envoyService:
            type: NodePort
    spec:
      provider:
        type: Kubernetes
        kubernetes:
          envoyService:
            type: NodePort
            patch:
              type: StrategicMerge
              value:
                spec:
                  ports:
                  - name: http-80
                    nodePort: 30080
                    port: 80
  YAML

  depends_on = [
    kubectl_manifest.gateway_api_crds,
    helm_release.gateway_api
  ]
}

resource "kubectl_manifest" "gateway_class" {
  yaml_body = <<-YAML
    apiVersion: gateway.networking.k8s.io/v1
    kind: GatewayClass
    metadata:
      name: eg
    spec:
      controllerName: gateway.envoyproxy.io/gatewayclass-controller
      parametersRef:
        group: gateway.envoyproxy.io
        kind: EnvoyProxy
        name: custom-proxy-config
        namespace: ${var.gateway_api_namespace}
  YAML

  depends_on = [
    kubectl_manifest.gateway_api_crds,
    kubectl_manifest.envoy_proxy,
    helm_release.gateway_api
  ]
}

# Gateway с правильным allowedRoutes
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
          allowedRoutes:
            namespaces:
              from: All
  YAML

  depends_on = [
    kubectl_manifest.gateway_api_crds,
    kubectl_manifest.gateway_class,
    kubectl_manifest.envoy_proxy,
    helm_release.gateway_api
  ]
}