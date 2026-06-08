locals {
  ###
  # Get configs
  ###
  talosconfig_path_1 = "~/.talos/config"
  talosconfig_path_2 = "~/.talos/talosconfig"

  talosconfig_exists_1 = fileexists(local.talosconfig_path_1)
  talosconfig_exists_2 = fileexists(local.talosconfig_path_2)

  talos_config = local.talosconfig_exists_1 ? yamldecode(file(local.talosconfig_path_1)) : (
    local.talosconfig_exists_2 ? yamldecode(file(local.talosconfig_path_2)) : null
  )
  #
  talos_context       = local.talos_config.context
  talos_endpoint_port = "6443"
  talos_endpoint_ip   = toset(local.talos_config.contexts[local.talos_context].endpoints)

  ###
  # 
  ###
  talos_patch = {
    cluster = {
      network = {
        cni = {
          name = "none"
        }
      }
      proxy = {
        disabled = true
      }
    }
    machine = {
      registries = {
        mirrors = {
          "registry.k8s.io" = {
            endpoints = [
              "https://k8s.kubesre.xyz",
              "https://registry-k8s-io.mirrors.sjtug.sjtu.edu.cn",
              "https://k8s.nju.edu.cn"
            ]
          }
        }
      }
    }
  }

}
