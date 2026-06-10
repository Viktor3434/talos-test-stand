###
# Get Talos secret.yaml
###
import {
  to = module.del-flannel.talos_machine_secrets.machine_secrets
  id = pathexpand("~/.talos/secrets.yaml")
}