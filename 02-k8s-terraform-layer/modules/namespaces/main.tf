resource "kubernetes_namespace" "default_ns" {
  for_each = toset(var.namespaces)

  metadata {
    name = each.value
  }
}


resource "kubernetes_namespace_v1" "privileged_ns" {
  for_each = toset(var.privileged_namespaces)

  metadata {
    name = each.value
    labels = {
      "pod-security.kubernetes.io/enforce" = "privileged"
      # "pod-security.kubernetes.io/warn"    = "baseline"
      # "pod-security.kubernetes.io/audit"   = "baseline"
    }
  }
}