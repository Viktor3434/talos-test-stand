module "del-flannel" {
  source = "./modules/del-flannel"
}

module "namespaces" {
  source = "./modules/namespaces"
}

module "cni-install" {
  source = "./modules/cni-install"
  depends_on = [module.del-flannel]
}
