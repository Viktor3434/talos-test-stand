###
# Create patch
###

data "talos_machine_configuration" "controlplane" {
  for_each = local.talos_endpoint_ip

  cluster_name     = local.talos_context
  machine_type     = "controlplane"
  cluster_endpoint = "https://${each.value}:${local.talos_endpoint_port}"
  machine_secrets  = talos_machine_secrets.machine_secrets.machine_secrets

  kubernetes_version = "v1.35.4"
}

resource "talos_machine_secrets" "machine_secrets" {}

###
# Apply patch
###

resource "talos_machine_configuration_apply" "control_plane" {
  for_each = local.talos_endpoint_ip

  client_configuration        = talos_machine_secrets.machine_secrets.client_configuration
  machine_configuration_input = data.talos_machine_configuration.controlplane[each.key].machine_configuration
  node                        = each.value

  config_patches = [yamlencode(local.talos_patch)]
}


###
# Delete daemonsets
###
resource "null_resource" "remove_legacy_daemonsets" {
  depends_on = [
    talos_machine_configuration_apply.control_plane
  ]

  provisioner "local-exec" {
    command = <<-EOF
      echo "Waiting for Kubernetes API after Talos config apply..."
      for i in {1..30}; do
        kubectl --kubeconfig ~/.kube/config get nodes &>/dev/null && break
        echo "API not ready, waiting... ($$i/30)"
        sleep 10
      done
      kubectl --kubeconfig ~/.kube/config -n kube-system delete daemonset kube-proxy kube-flannel --ignore-not-found=true
      echo "Legacy daemonsets removed."
    EOF
  }

  triggers = {
    patch_applied = yamlencode(local.talos_patch)
  }
}