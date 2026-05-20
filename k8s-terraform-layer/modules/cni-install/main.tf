# # cilium.tf

# resource "helm_release" "cilium" {
#   name             = "cilium"
#   repository       = "https://helm.cilium.io/"
#   chart            = "cilium"
#   version          = "1.16.5"               # последняя стабильная версия (проверьте)
#   namespace        = "kube-system"
#   create_namespace = false                  # kube-system уже существует

#   set {
#     name  = "ipam.mode"
#     value = "kubernetes"
#   }

#   set {
#     name  = "kubeProxyReplacement"
#     value = "true"
#   }

#   set {
#     name  = "securityContext.capabilities.ciliumAgent"
#     value = "{CHOWN,KILL,NET_ADMIN,NET_RAW,IPC_LOCK,SYS_ADMIN,SYS_RESOURCE,DAC_OVERRIDE,FOWNER,SETGID,SETUID}"
#   }

#   set {
#     name  = "securityContext.capabilities.cleanCiliumState"
#     value = "{NET_ADMIN,SYS_ADMIN,SYS_RESOURCE}"
#   }

#   set {
#     name  = "cgroup.hostRoot"
#     value = "/sys/fs/cgroup"
#   }

#   set {
#     name  = "k8sServiceHost"
#     value = "127.0.0.1"      # или IP вашей master-ноды, если kubelet не на 127.0.0.1
#   }

#   set {
#     name  = "k8sServicePort"
#     value = "7445"            # стандартный порт API Talos (не 6443, т.к. Cilium подменяет kube-proxy)
#   }
# }