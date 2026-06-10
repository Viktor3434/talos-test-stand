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
        repoURL        = "https://github.com/Viktor3434/talos-terraform-argocd.git"
        targetRevision = "main"
        path           = "03-k8s-gitops-layer/apps-test-env"
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