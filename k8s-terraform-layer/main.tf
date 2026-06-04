module "del-flannel" {
  source = "./modules/del-flannel"
}

module "namespaces" {
  source = "./modules/namespaces"
}

module "cni-install" {
  source     = "./modules/cni-install"
  depends_on = [module.del-flannel]
}

module "helm-charts-infra" {
  source = "./modules/helm-charts-infra"

  gateway_api_namespace = module.namespaces.gateway_api_namespace
  argocd_namespace      = module.namespaces.argocd_namespace

  depends_on = [
    module.namespaces,
    module.cni-install
  ]
}