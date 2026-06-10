# 📄 README: Terraform Layer (`02-k8s-terraform-layer`)

> Инфраструктура как код для управления кластером Talos Linux: установка CNI, настройка namespaces, деплой инфраструктурных Helm-чартов и интеграция с ArgoCD.

---

## 📋 Оглавление

- [Требования](#-требования)
- [Структура проекта](#-структура-проекта)
- [Быстрый старт](#-быстрый-старт)
- [Модули](#-модули)
- [Управление состоянием](#-управление-состоянием)
- [Переменные и конфигурация](#-переменные-и-конфигурация)
- [Интеграция с GitOps](#-интеграция-с-gitops)
- [Troubleshooting](#-troubleshooting)

---

## ⚙️ Требования

| Инструмент | Версия | Примечание |
|------------|--------|------------|
| `terraform` | `>= 1.15.3` | [Скачать](https://developer.hashicorp.com/terraform/downloads) |
| `kubectl` | `~1.30+` | Для отладки и `kubectl`-провайдера |
| `talosctl` | `~1.7+` | Опционально, для ручной работы с кластером |
| `kubeconfig` | — | Файл `~/.kube/config` с контекстом `admin@talos-cluster` |
| `Talos secrets` | — | Файл `~/.talos/secrets.yaml` (импортируется) |

---

## 📁 Структура проекта

```text
02-k8s-terraform-layer/
├── main.tf                 # Точка входа: вызов модулей
├── provider.tf             # Конфигурация провайдеров
├── import.tf               # Импорт существующих секретов Talos
├── variables.tf            # (опционально) Входные переменные
├── outputs.tf              # (опционально) Экспортируемые значения
└── modules/
    ├── del-flannel/        # Удаление Flannel + патчинг Talos
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── namespaces/         # Создание namespace'ов
    │   ├── main.tf
    │   └── outputs.tf
    ├── cni-install/        # Установка нового CNI-плагина
    │   └── main.tf
    └── helm-charts-infra/  # Деплой инфраструктурных чартов
        ├── main.tf
        ├── variables.tf
        └── charts/         # Локальные .tgz архивы чартов
```

---

## 🚀 Быстрый старт

### 1. Инициализация

```bash
cd 02-k8s-terraform-layer
terraform init
```

### 2. Планирование
```bash
terraform plan -out=tfplan
```

### 3. Применение
```bash
terraform apply tfplan
```
### 4. Проверка
```bash
kubectl get pods -A
kubectl get nodes
talosctl get members
```

## 🧩 Модули
- modules/namespaces \
Создаёт Kubernetes namespaces с поддержкой Pod Security Standards.
- modules/del-flannel \
**удаляет стандартный Flannel CNI и применяет кастомные патчи к конфигурации узлов Talos.**
- modules/cni-install \
Устанавливает новый CNI-плагин (Calico/Cilium/другой) после удаления Flannel. \
Зависимости: `depends_on = [module.del-flannel]`
- modules/helm-charts-infra \
Деплоит инфраструктурные компоненты через Helm:

| Компонент       | Назначение        | Источник                     |
|-----------------|-------------------|------------------------------|
| MetalLB         | L2 LoadBalancer   | Helm repo                    |
| Gateway API     | CRDs + manifests  | Helm repo                    |
| ArgoCD          | GitOps-контроллер | Локальный charts/argo-cd-*.tgz |
| Metrics Server  | Метрики для HPA   | Helm repo                    |

Дополнительно modules/helm-charts-infra создаёт в ArgoCD:
- AppProject "main" — политики доступа для CI/CD
- Application "apps" — ссылка на k8s-gitops-layer/apps-test-env для синхронизации приложений

## 💾 Управление состоянием
Импорт секретов Talos
Файл import.tf импортирует существующие секреты, чтобы Terraform не пытался их пересоздать:
```hcl
import {
  to = module.del-flannel.talos_machine_secrets.machine_secrets
  id = pathexpand("~/.talos/secrets.yaml")
}
```

## 🔗 Интеграция с GitOps
```
Terraform настраивает ArgoCD для дальнейшей синхронизации:
02-k8s-terraform-layer (IaC)
         ↓
[создаёт] ArgoCD Application "apps"
         ↓
k8s-gitops-layer/apps-test-env (GitOps)
         ↓
[синхронизирует] приложения в кластер
```

## 📜 Лицензия
MIT — используйте на свой страх и риск. Автор не несёт ответственности за потерю данных в продакшен-кластерах.