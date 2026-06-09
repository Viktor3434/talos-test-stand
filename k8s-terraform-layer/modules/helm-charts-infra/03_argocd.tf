resource "helm_release" "argocd" {
  name = "argocd"
  # repository       = "https://argoproj.github.io/argo-helm"
  chart = "${path.module}/charts/argo-cd-9.5.20.tgz"
  # version          = "9.5.20"
  namespace        = var.argocd_namespace
  create_namespace = false

  values = [
    file("${path.module}/values/argocd.yaml")
  ]

  depends_on = [
    helm_release.gateway_api,
    kubectl_manifest.gateway_api_crds,
    kubectl_manifest.gateway_class,
    kubectl_manifest.gateway,
  ]

  lifecycle {
    prevent_destroy = false
  }
}

#####
### Argo resouces
#####

resource "kubernetes_manifest" "argocd_appproject_main" {
  manifest = {
    apiVersion = "argoproj.io/v1alpha1"
    kind       = "AppProject"
    metadata = {
      name      = "main"
      namespace = "argocd"
    }
    spec = {
      description = "Main Project"
      sourceRepos = ["*"]
      destinations = [{
        namespace = "*"
        server    = "https://kubernetes.default.svc"
      }]
      clusterResourceWhitelist = [{
        group = "*"
        kind  = "*"
      }]
      namespaceResourceWhitelist = [{
        group = "*"
        kind  = "*"
      }]
      orphanedResources = {
        warn = false
      }
      roles = [{
        description = "ci role for all apps"
        name        = "ci-role"
        policies = [
          "p, proj:main:ci-role, applications, get, main/*, allow",
          "p, proj:main:ci-role, applications, sync, main/*, allow",
        ]
      }]
    }
  }

  depends_on = [
    helm_release.argocd,
  ]
}

resource "kubernetes_manifest" "argocd_application_apps" {
  manifest = {
    apiVersion = "argoproj.io/v1alpha1"
    kind       = "Application"
    metadata = {
      name      = "apps"
      namespace = "argocd"
    }
    spec = {
      project = "main"
      source = {
        repoURL        = "https://github.com/Viktor3434/talos-test-stand.git"
        targetRevision = "main"
        path           = "k8s-gitops-layer/apps-test-env"
        helm = {
          valueFiles = ["values.yaml", "values-extra.yaml"]
        }
      }
      destination = {
        namespace = "argocd"
        server    = "https://kubernetes.default.svc"
      }
      syncPolicy = {
        automated = {
          prune    = true
          selfHeal = true
        }
      }
    }
  }

  depends_on = [
    helm_release.argocd,
    kubernetes_manifest.argocd_appproject_main,
  ]
}