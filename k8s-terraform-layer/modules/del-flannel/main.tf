###
# Create patch
###

data "talos_machine_configuration" "controlplane" {
  for_each = local.talos_endpoint_ip

  cluster_name     = local.talos_context
  machine_type     = "controlplane"
  cluster_endpoint = "https://${each.value}:${local.talos_endpoint_port}"
  machine_secrets  = talos_machine_secrets.machine_secrets.machine_secrets
}

resource "talos_machine_secrets" "machine_secrets" {}

###
# Apply patch
###

resource "talos_machine_configuration_apply" "control_plane" {
  for_each = local.talos_endpoint_ip

  client_configuration = talos_machine_secrets.machine_secrets.client_configuration
  machine_configuration_input = data.talos_machine_configuration.controlplane[each.key].machine_configuration
  node = each.value

  config_patches = [
    yamlencode({
      cluster = {
        network = {
          cni = {
            name = "none" # disable CNI Flannel
          }
        }
        proxy = {
          disabled = true # disable kube-proxy (use Cilium)
        }
      }
    })
  ]
}