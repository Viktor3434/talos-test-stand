# talos-terraform-argocd

Этот репозиторий предоставляет полностью автоматизированный тестовый стенд для развёртывания Kubernetes-кластера на базе Talos Linux с использованием GitOps и ArgoCD. Всё управление инфраструктурой и приложениями происходит декларативно через код.

## 🎯 Основная цель

- Infrastructure as Code (IaC): автоматизация создания и настройки Talos-кластера на виртуальных машинах.
- GitOps для приложений: все конфигурации Kubernetes хранятся в Git и синхронизируются с кластером через ArgoCD.
- Полная воспроизводимость: возможность поднять или уничтожить весь стенд одной командой (почти).

## 📁 Структура репозитория

```text
## 📁 Структура репозитория

    talos-terraform-argocd/
    ├── demo-chart-in-git-repo/              # Для примера в ArgoCD (условно это корень другого репозитория)
    │   ├── example-app-code/                # Директория с пустым файлом
    │   ├── .helm/                           # Директория с чартом для проекта
    │   └── .values/                         # Директория с values файлом
    │
    ├── k8s-gitops-layer/                    # GitOps-слой (ArgoCD + App of Apps)
    │   ├── apps-test-env/                   # Helm-чарт в котором генерируются "дочерние" чарты (App of Apps)
    │   │   ├── templates/                   # Шаблоны ArgoCD-app, HTTPRoute, Namespaces
    │   │   ├── values.yaml                  # 
    │   │   └── values-extra.yaml            # Для дополнительных манифестов (напрмер если в чарте не предусмотрен HttpRoute для api gateway)
    │   ├── values-test-env/                 # Значения для конкретных приложений (в случае если мы values держим отдельно от приложения)
    │   │   └── podinfo.yaml
    │   └── README.md
    │
    ├── k8s-terraform-layer/                 # Terraform-слой для развёртывания инфраструктурных компонентов в кластере
    │   ├── modules/
    │   │   ├── cni-install/                 # Установка CNI (Cilium)
    │   │   ├── del-flannel/                 # Удаление flannel (если требуется)
    │   │   ├── helm-charts-infra/           # Установка ArgoCD, MetalLB, Gateway API, Metrics Server
    │   │   └── namespaces/                  # Создание неймспейсов через Terraform
    │   ├── provider.tf
    │   ├── main.tf
    │   ├── import.tf
    │   └── README.md
    │
    ├── talos-test-stand-up/                 # Логика поднятия Talos-кластера (Vagrant + Python)
    │   ├── Vagrantfile                      # Конфигурация виртуальных машин (генерируется из .j2)
    │   ├── Vagrantfile.j2                   # Шаблон Vagrantfile
    │   ├── run_all.py                       # Главный оркестратор (запуск всех шагов)
    │   ├── 01_check_and_vagrant_up.py       # Проверка окружения и `vagrant up`
    │   ├── 02_install_masters.py            # Установка Talos на control-plane узлы
    │   ├── 03_install_workers.py            # Подключение worker-узлов
    │   ├── 00_destroy_vm.py                 # Полное удаление ВМ
    │   ├── config.py                        # Конфигурация (IP, пути, версии)
    │   ├── utils/                           # Вспомогательные модули (чеки, команды, libvirt, talos)
    │   └── README.md
    │
    └── README.md                            # Этот файл
```

## 🧱 Ключевые компоненты

### 1️⃣ Infrastructure Layer (развёртывание кластера)
- Vagrant + libvirt — создание виртуальных машин.
- Python‑скрипты — последовательная установка Talos, bootstrap control‑plane, подключение worker‑узлов.
- **Результат:** готовый Talos-кластер с настроенными `kubeconfig` и `talosconfig`.

### 2️⃣ GitOps Layer (управление приложениями)
- ArgoCD — синхронизация состояния кластера с Git.
- Helm — упаковка и параметризация приложений.
- Паттерн **App of Apps** — декларативное описание всех приложений в одном месте.
- Gateway API (Cilium) — управление входящим трафиком через HTTPRoute.

Подробнее: см. `k8s-gitops-layer/README.md`.

## ⚙️ Требования для использования GitOps-слоя

Если у вас уже есть работающий кластер, для применения GitOps-слоя необходимо:

- Установленный ArgoCD в кластере.
- `kubectl` с доступом к кластеру.
- Helm 3.14+.
- Доступ к этому Git-репозиторию изнутри кластера.

## 🔧 Полный цикл развёртывания (включая создание кластера)

Если вы хотите автоматически развернуть весь стенд (VM + Talos + ArgoCD + приложения), следуйте инструкциям из ранее существовавшей директории `talos-test-stand-up`. Этот процесс включает:

- Проверку окружения (Vagrant, libvirt, `talosctl`).
- Запуск `vagrant up`.
- Установку Talos на master-узлы и bootstrap.
- Подключение worker-узлов.
- Установку ArgoCD через Terraform (или вручную).
- Настройку GitOps-слоя.

> В текущей версии эти шаги могут быть вынесены в отдельный репозиторий или объединены с Terraform-провайдерами. Для получения актуальной информации проверьте наличие директории `talos-test-stand-up` или обратитесь к истории коммитов.

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. Подробности смотрите в файле LICENSE.

## Связанные ресурсы

- [ArgoCD: App of Apps Pattern](https://argo-cd.readthedocs.io/en/stable/operator-manual/cluster-bootstrapping/)
- [Talos Linux Documentation](https://www.talos.dev/)
- [Vagrant + libvirt руководство](https://vagrant-libvirt.github.io/vagrant-libvirt/)