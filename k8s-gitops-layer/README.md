# 📄 README: GitOps Layer (`k8s-gitops-layer`)

> GitOps-управление приложениями на базе ArgoCD: реализация паттерна "App of Apps", декларативное конфигурирование через Helm-чарты и управление сетевыми маршрутами.

---

## 📋 Оглавление

- [Требования](#-требования)
- [Структура проекта](#-структура-проекта)
- [Архитектура GitOps: паттерн App of Apps](#-архитектура-gitops-паттерн-app-of-apps)
- [Управление приложениями](#-управление-приложениями)
- [Конфигурация окружений](#-конфигурация-окружений)
- [Управление трафиком (HTTPRoute)](#-управление-трафиком-httproute)
- [Интеграция с Cilium Gateway API](#-интеграция-с-cilium-gateway-api)
- [Troubleshooting](#-troubleshooting)

---

## ⚙️ Требования

| Инструмент | Версия | Примечание |
|------------|--------|------------|
| `kubectl` | `~1.30+` | Для отладки и управления кластером |
| `ArgoCD` | `v2.10+` | Установлен в кластере (через `02-k8s-terraform-layer`) |
| `kubeconfig` | — | Файл `~/.kube/config` с контекстом `admin@talos-cluster` |
| `helm` | `~3.14+` | Для локальной отладки чартов |
| Git-доступ | — | Доступ к репозиторию `https://github.com/Viktor3434/talos-terraform-argocd.git` |

---

## 📁 Структура проекта

```text
k8s-gitops-layer/
├── apps-test-env/              # Helm-чарт "app-of-apps" для тестового окружения
│   ├── Chart.yaml              # Метаданные чарта
│   ├── values.yaml             # Values с настройками Argo application: приложения, репозитории
│   ├── values-extra.yaml       # Дополнительные k8s ресурсы (например: HTTPRoute), будут созданы из main app 
│   └── templates/              # Шаблоны ArgoCD-ресурсов
│       ├── application.yaml    # Генерация ArgoCD Application для каждого приложения
│       ├── httproute.yaml      # Генерация HTTPRoute (Gateway API), дополнительный ресурс.
│       └── namespaces.yaml     # Пре-создание namespace'ов с sync-wave -1
└── values-test-env/            # Переопределения значений для тестового окружения
    └── podinfo.yaml            # Helm-values для приложения podinfo
```

## 🏗️ Архитектура GitOps: паттерн App of Apps

В этом слое реализован паттерн **"App of Apps"** — стандартный подход GitOps для управления множеством приложений через один родительский манифест.

**Как это работает:**

1. Корневое приложение (`app-of-apps-test-env`) развернуто в ArgoCD вручную (из Terraform).
2. Оно отслеживает Helm-чарт `apps-test-env` в Git-репозитории.
3. Helm-чарт генерирует манифесты `ArgoCD Application` для каждого приложения, объявленного в `values.yaml`.
4. Дочерние приложения указывают на свои Helm-чарты и значения (например, `podinfo` из `values-test-env/podinfo.yaml`).
5. При изменении любого значения в Git ArgoCD автоматически синхронизирует только затронутое приложение.

Такой подход обеспечивает:

- ✅ **Модульность** — каждое приложение имеет свою конфигурацию.
- ✅ **Прозрачность** — все изменения проходят через Git (Single Source of Truth).
- ✅ **Автоматическое восстановление** — при ручных изменениях ArgoCD возвращает желаемое состояние (self-healing).
- ✅ **Масштабируемость** — добавление нового приложения сводится к добавлению одной секции в `values.yaml`.

## 📦 Управление приложениями

### Формат описания приложения

В файле `values.yaml` приложения объявляются в секции `applications`:

```yaml
applications:
  - name: "podinfo"                     # Имя приложения (используется как chartName по умолчанию)
    namespace: "example-app"            # Целевой namespace
    chartRepo: "https://stefanprodan.github.io/podinfo"  # URL Helm-репозитория
    targetRevision: "6.13.0"            # Версия чарта
    automated:                          # Автоматическая синхронизация
      prune: true
      selfHeal: true
    syncOptions:
      - "ServerSideApply=true"
    helm:                               # Переопределение values
      valueFiles:
        - "$values/k8s-gitops-layer/values-test-env/podinfo.yaml"
```
либо:

```yaml
applications:
  - name: "podinfo-from-git"
    namespace: "example-app"
    chartFromGitRepo: true
    gitRepoPath: "demo-chart-in-git-repo/.helm"
    chartRepo: "https://github.com/Viktor3434/talos-terraform-argocd.git"
    chartName: "podinfo"                                           
    valuesRepo:
      url: https://github.com/Viktor3434/talos-terraform-argocd.git
      revision: main
    helm:
      valueFiles:
        - $values/demo-chart-in-git-repo/.values/values.yaml
    targetRevision: main
    automated:
      prune: true
      selfHeal: true
```

### Параметры приложения

| Поле | Описание | Значение по умолчанию |
|------|----------|------------------------|
| `name` | Имя приложения и release name | Обязательное |
| `namespace` | Kubernetes namespace для деплоя | Имя приложения |
| `chartRepo` | URL Helm-репозитория | `global.chartRepo.repoURL` |
| `chartName` | Имя чарта (если отличается от `name`) | `name` |
| `targetRevision` | Версия чарта | Обязательное |
| `automated.prune` | Удалять ресурсы при удалении приложения | `false` |
| `automated.selfHeal` | Автоматически исправлять дрейф | `false` |
| `syncOptions` | Дополнительные опции синхронизации | `[]` |
| `helm.valueFiles` | Список values-файлов (поддерживает `$values/`) | Автоматический путь |

## 🌍 Конфигурация окружений

### Глобальные параметры

В `values.yaml` определены глобальные настройки:

```yaml
global:
  environment: "test-env"                       # Имя окружения
  server: "https://kubernetes.default.svc"     # Kubernetes API server
  project: "main"                              # ArgoCD project
  chartRepo:
    repoURL: "https://charts.bitnami.com/bitnami"  # Репозиторий чартов по умолчанию
  valuesRepo:
    url: "https://github.com/Viktor3434/talos-terraform-argocd.git"
    revision: "main"
```

### Values-файлы для окружений

Для каждого окружения (`test-env`, `prod-env`) можно создать отдельную директорию с values-файлами:

```text
values-test-env/
├── podinfo.yaml         # Значения для podinfo в test-env
└── another-app.yaml     # Значения для другого приложения
```

Шаблон `application.yaml` автоматически подставляет values-файл по пути:

```text
$values/k8s-gitops-layer/values-{{ $.Values.global.environment }}/{{ $appName }}.yaml
```

## 🌐 Управление трафиком (HTTPRoute)

Слой поддерживает декларативное создание ресурсов **HTTPRoute** (Gateway API) для организации входящего трафика.

### Конфигурация HTTPRoute

В файле `values-extra.yaml`:

```yaml
httpRoutes:
  podinfo-main:
    namespace: example-app
    hostnames:
      - "podinfo.local"
      - "*.example.com"
    parentRefs:
      - name: eg                      # Имя Gateway
        namespace: envoy-gateway-system
        sectionName: http             # Имя listener'а
    rules:
      - matches:
          - path:
              type: PathPrefix
              value: /
        backendRefs:
          - name: podinfo             # Имя Service
            port: 9898
            weight: 1
```

Шаблон `httproute.yaml` генерирует ресурс `HTTPRoute` для каждой записи в `httpRoutes`.

### Параметры HTTPRoute

| Поле | Описание |
|------|----------|
| `namespace` | Namespace, где будет создан HTTPRoute |
| `hostnames` | Список доменных имен для маршрутизации |
| `parentRefs` | Ссылка на Gateway (обычно Cilium Envoy Gateway) |
| `rules.matches` | Правила сопоставления путей |
| `rules.backendRefs` | Целевой Service, порт и вес |

## 🔌 Интеграция с Cilium Gateway API

Этот слой тесно интегрируется с **Cilium Gateway API**, установленным через `02-k8s-terraform-layer`. Cilium обеспечивает:

- Envoy Gateway как контроллер ingress-трафика.
- HTTPRoute как декларативный способ настройки маршрутизации.
- Безопасность L7 с mTLS и политиками авторизации.

Все HTTPRoute-ресурсы автоматически синхронизируются ArgoCD и применяются Cilium без дополнительных шагов.

## 🛠️ Troubleshooting

### 1. ArgoCD не видит репозиторий

```bash
# Проверьте подключение к репозиторию
argocd repo list
# Переподключитесь с правильными учетными данными
argocd repo add https://github.com/Viktor3434/talos-terraform-argocd.git --username <user> --password <token>
```

### 2. Приложение в статусе "OutOfSync"

```bash
# Просмотрите различия
argocd app diff app-podinfo-ns-example-app
# Принудительная синхронизация
argocd app sync app-podinfo-ns-example-app
```

### 3. Ошибка Invalid value: "$values/..." — values-файл не найден

Убедитесь, что путь в `helm.valueFiles` корректен и файл существует в репозитории:

```bash
# Проверьте наличие файла
argocd repo get https://github.com/Viktor3434/talos-terraform-argocd.git --path k8s-gitops-layer/values-test-env/podinfo.yaml
```

### 4. HTTPRoute не активен (Cilium Gateway не найден)

```bash
# Проверьте, что Gateway существует в указанном namespace
kubectl get gateway -n envoy-gateway-system
# Проверьте статус HTTPRoute
kubectl get httproute -n example-app podinfo-main -o yaml
```

### 5. Сбой синхронизации из-за отсутствующего namespace

Убедитесь, что в `values.yaml` указаны namespace'ы в секции `namespaces`:

```yaml
namespaces:
  - example-app
  - other-namespace
```

Эти namespace'ы будут созданы с `sync-wave: -1` до развертывания приложений.

### 6. Очистка всех ресурсов

```bash
# Удалите корневое приложение (удалит все дочерние автоматически)
argocd app delete app-of-apps-test-env --cascade
# Либо удалите через kubectl
kubectl delete application -n argocd -l app.kubernetes.io/instance=app-of-apps-test-env
```

## 🔗 Связанные ресурсы

- [ArgoCD: App of Apps Pattern](https://argo-cd.readthedocs.io/en/stable/operator-manual/cluster-bootstrapping/)
- [Helm Chart для apps-test-env](./apps-test-env/)
- [Terraform-слой для установки CNI и ArgoCD](../02-k8s-terraform-layer/)

## 📜 Лицензия
MIT — используйте на свой страх и риск. Автор не несёт ответственности за потерю данных в продакшен-кластерах.