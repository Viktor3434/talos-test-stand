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
  talos_context = local.talos_config.context
  talos_endpoint_port = "6443"
  talos_endpoint_ip = toset(local.talos_config.contexts[local.talos_context].endpoints)
}



######
###### TMP save
######

# locals {
#   ###
#   # Get secrets
#   ###
#   talos_secrets = yamldecode(file("~/.talos/secrets.yaml"))

#   etcd_cert              = local.talos_secrets.certs.etcd.crt
#   etcd_key               = local.talos_secrets.certs.etcd.key
#   k8s_cert               = local.talos_secrets.certs.k8s.crt
#   k8s_key                = local.talos_secrets.certs.k8s.key
#   k8s_aggregator_cert    = local.talos_secrets.certs.k8saggregator.crt
#   k8s_aggregator_key     = local.talos_secrets.certs.k8saggregator.key
#   k8s_serviceaccount_key = local.talos_secrets.certs.k8sserviceaccount.key
#   os_cert                = local.talos_secrets.certs.os.crt
#   os_key                 = local.talos_secrets.certs.os.key


#   cluster_id     = local.talos_secrets.cluster.id
#   cluster_secret = local.talos_secrets.cluster.secret

#   secrets_bootstraptoken            = local.talos_secrets.secrets.bootstraptoken
#   secrets_secretboxencryptionsecret = local.talos_secrets.secrets.secretboxencryptionsecret

#   trustdinfo = local.talos_secrets.trustdinfo.token
# }


# data "talos_machine_configuration" "controlplane" {
#   for_each = local.talos_endpoint_ip

#   cluster_name     = local.talos_context
#   machine_type     = "controlplane"
#   cluster_endpoint = "https://${each.value}:${local.talos_endpoint_port}"
#   machine_secrets = {
#     certs = {
#       etcd               = { cert = local.etcd_cert, key = local.etcd_key },
#       k8s                = { cert = local.k8s_cert, key = local.k8s_key },
#       k8s_aggregator     = { cert = local.k8s_aggregator_cert, key = local.k8s_aggregator_key },
#       k8s_serviceaccount = { key = local.k8s_serviceaccount_key },
#       os                 = { cert = local.os_cert, key = local.os_key },

#     }
#     cluster = {
#       id     = local.cluster_id
#       secret = local.cluster_secret
#     }
#     secrets = {
#       bootstrap_token             = local.secrets_bootstraptoken
#       secretbox_encryption_secret = local.secrets_secretboxencryptionsecret
#     }
#     trustdinfo = {
#       token = local.trustdinfo
#     }
#   }


# }