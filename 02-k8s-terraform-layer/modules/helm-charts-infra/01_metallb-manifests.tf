resource "kubectl_manifest" "metallb_ipaddresspool" {
  yaml_body = <<-YAML
    apiVersion: metallb.io/v1beta1
    kind: IPAddressPool
    metadata:
      name: default-pool
      namespace: metallb
    spec:
      addresses:
      - "192.168.121.110-192.168.121.250"
  YAML

  depends_on = [
    helm_release.metallb
  ]
}

resource "kubectl_manifest" "metallb_l2advertisement" {
  yaml_body = <<-YAML
    apiVersion: metallb.io/v1beta1
    kind: L2Advertisement
    metadata:
      name: default-l2-adv
      namespace: metallb
    spec:
      ipAddressPools:
      - default-pool
  YAML

  depends_on = [
    kubectl_manifest.metallb_ipaddresspool
  ]
}