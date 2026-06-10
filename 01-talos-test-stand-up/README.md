# Talos Linux Test Stand

Автоматизированное развёртывание тестового кластера Talos Linux на виртуальных машинах с использованием Vagrant и libvirt.

Этот инструмент представляет собой набор Python-скриптов, которые последовательно проходят все этапы создания кластера: от проверки окружения до инициализации control-plane и подключения worker-узлов. Вся логика вынесена в переиспользуемые модули, а единый оркестратор позволяет выполнить полный цикл одной командой.

**Важно:** Стенд предназначен для разработки и тестирования. Не используйте эту конфигурацию в production-средах.

---

## 📋 Содержание

- [Требования](#-требования)
- [Установка и настройка](#-установка-и-настройка)
- [Быстрый старт](#-быстрый-старт)
- [Структура проекта](#-структура-проекта)
- [Пошаговое использование (для отладки)](#-пошаговое-использование-для-отладки)
- [Конфигурация](#-конфигурация)
- [Устранение неполадок](#-устранение-неполадок)
- [Лицензия](#-лицензия)

---

## ⚙️ Требования

Перед началом работы убедитесь, что ваша система соответствует следующим требованиям:

- **ОС:** Linux с установленным KVM и libvirt.
- **Vagrant:** версия 2.2+ и плагин `vagrant-libvirt`.
- **Python:** версия 3.7+ (используются только модули стандартной библиотеки, дополнительные пакеты не требуются).
- **`talosctl`:** CLI-инструмент для управления Talos Linux (см. инструкцию по установке ниже).
- **`kubectl`:** (опционально) для проверки состояния кластера.
- **ISO-образ:** Talos Linux `metal-amd64.iso` (см. раздел загрузки).

---

## 🔧 Установка и настройка

### 1. Клонирование репозитория

```bash
git clone <url-репозитория> talos-terraform-argocd
cd talos-terraform-argocd/01-talos-test-stand-up
```

### 2. Установка зависимостей для Vagrant

Установите Vagrant согласно документации вашего дистрибутива. Затем добавьте плагин libvirt:

```bash
vagrant plugin install vagrant-libvirt
```

Убедитесь, что ваш пользователь состоит в группах `libvirt` и `kvm`:

```bash
sudo usermod -aG libvirt,kvm $USER
newgrp libvirt
```

### 3. Установка `talosctl`

Скачайте бинарный файл с GitHub и поместите его в `$PATH`:

```bash
curl -Lo /usr/local/bin/talosctl https://github.com/siderolabs/talos/releases/latest/download/talosctl-$(uname -s | tr '[:upper:]' '[:lower:]')-amd64
chmod +x /usr/local/bin/talosctl
```

### 4. Загрузка ISO-образа Talos

Поместите файл `metal-amd64.iso` в директорию `~/ISO-images/` (путь по умолчанию, можно изменить в `config.py`). Вы можете создать эту директорию и скачать образ с помощью команд:

```bash
mkdir -p ~/ISO-images
wget -O ~/ISO-images/metal-amd64.iso https://github.com/siderolabs/talos/releases/download/v1.13.0/metal-amd64.iso
```

### 5. Конфигурация (опционально)

Все настройки находятся в файле `config.py`. Вы можете изменить количество узлов, имена пулов и пути. Убедитесь, что конфигурация соответствует вашему Vagrantfile.

---

## 🚀 Быстрый старт

После выполнения всех шагов по установке и настройке запустите оркестратор из корня проекта:

```bash
python3 run_all.py
```

Оркестратор выполнит следующие шаги:

1. Проверит все зависимости и запустит `vagrant up`.
2. Дождётся получения IP-адресов виртуальными машинами.
3. Установит Talos на control plane узлы и инициализирует кластер.
4. Добавит worker-узлы в кластер.

В результате вы получите работающий кластер, а файлы конфигурации (`talosconfig` и `kubeconfig`) будут сохранены в `~/.talos/`.

Пример проверки кластера после завершения:

```bash
export KUBECONFIG=~/.talos/kubeconfig
kubectl get nodes
```

---

## 📁 Структура проекта

```text
.
├── 00_destroy_vm.py                # Уничтожение стенда (vagrant destroy + удаление дисков)
├── 01_check_and_vagrant_up.py      # Проверка зависимостей и запуск vagrant up
├── 02_install_masters.py           # Установка Talos на control plane узлы
├── 03_install_workers.py           # Добавление worker-узлов в кластер
├── run_all.py                      # Оркестратор: последовательный запуск всех шагов
├── config.py                       # Общие константы и настройки
├── Vagrantfile                     # Описание виртуальных машин для Vagrant
├── Vagrantfile.j2                  # Jinja-шаблон для генерации Vagrantfile
└── utils/                          # Модули с общими функциями
    ├── __init__.py
    ├── cmd.py                      # Запуск shell-команд
    ├── ui.py                       # Цветной вывод сообщений
    ├── libvirt.py                  # Работа с libvirt (пулы, тома, IP-адреса)
    ├── checks.py                   # Проверки окружения (сервисы, плагины, группы)
    └── talos.py                    # Взаимодействие с Talos (генерация конфигов, bootstrap)
```

---

## 🐞 Пошаговое использование (для отладки)

Если вам нужно выполнить шаги вручную (например, для отладки), вы можете запускать скрипты по отдельности.

### 0. Уничтожение предыдущего стенда (опционально)

Удаляет все виртуальные машины через Vagrant и очищает дисковые тома в пуле `pool-talos`.

```bash
python3 00_destroy_vm.py
```

### 1. Проверка и создание VM

Проверяет наличие необходимых команд, активность `libvirtd`, сеть, права пользователя, плагин Vagrant, наличие ISO-образа в пуле, а затем выполняет `vagrant up`.

```bash
python3 01_check_and_vagrant_up.py
```

### 2. Установка control plane

Определяет IP-адреса мастер-нод (имена содержат `cp`), генерирует `secrets.yaml` и конфигурации Talos, настраивает `talosconfig`, применяет `controlplane.yaml` к каждому мастеру, ожидает перезагрузки узлов, выполняет bootstrap и получает `kubeconfig`.

```bash
python3 02_install_masters.py
```

### 3. Добавление worker-узлов

Находит IP-адреса узлов, не содержащих `cp` в имени, применяет к ним `worker.yaml` и ожидает их появления в кластере (статус `Ready`).

```bash
python3 03_install_workers.py
```

---

## ⚙️ Конфигурация

Все параметры настраиваются в файле `config.py`. Вот основные из них:

| Параметр | Значение по умолчанию | Описание |
|----------|------------------------|----------|
| `CLUSTER_NAME` | `"talos-cluster"` | Имя кластера Talos |
| `NETWORK_NAME` | `"default"` | Имя виртуальной сети libvirt |
| `CONTROL_PLANES_COUNT` | `1` | Ожидаемое количество master-нод |
| `WORKERS_COUNT` | `2` | Ожидаемое количество worker-нод |
| `TALOS_CONF_DIR` | `~/.talos` | Каталог для хранения secrets.yaml, конфигов и kubeconfig |
| `ISO_PATH` | `~/ISO-images/metal-amd64.iso` | Путь к ISO-образу Talos |
| `POOL_ISO_NAME` | `"pool"` | Имя libvirt-пула для ISO-образов |
| `POOL_ISO_TARGET` | `~/ISO-images` | Путь к директории пула ISO на хост-машине |
| `POOL_DISKS_NAME` | `"pool-talos"` | Имя libvirt-пула для дисков виртуальных машин |
| `POOL_DISKS_TARGET` | `~/VirtualMachines/TalOS-linux` | Путь к директории пула дисков на хост-машине |
| `ISO_VOL_NAME` | `"metal-amd64.iso"` | Имя тома с ISO-образом в пуле |
| `LIBVIRT_NETWORK` | `"default"` | Виртуальная сеть для DHCP (алиас для `NETWORK_NAME`) |
| `REQUIRED_GROUPS` | `["libvirt"]` | Группы, в которых должен состоять пользователь |

Измените значения в `config.py` в соответствии с вашим окружением и Vagrantfile.

---

## 🔍 Устранение неполадок

| Проблема | Возможное решение |
|----------|-------------------|
| `vagrant: command not found` | Установите Vagrant. |
| `Please install the vagrant-libvirt plugin` | Выполните `vagrant plugin install vagrant-libvirt`. |
| `Failed to connect to libvirt` | Убедитесь, что пользователь состоит в группе `libvirt` и сервис `libvirtd` запущен: `sudo systemctl start libvirtd`. |
| Тома или пулы не создаются | Проверьте пути в `config.py` и наличие прав на запись в указанные директории. |
| Машины не получают IP | Убедитесь, что сеть `libvirt` `default` активна, и в ней включён DHCP. Проверить можно командой `sudo virsh net-list --all`. |
| Ошибка при применении конфигурации Talos | Проверьте наличие и актуальность ISO-образа. Убедитесь, что `talosctl` установлен и доступен в `$PATH`. |
| Bootstrap зависает или не завершается | Проверьте, что все control plane узлы успешно загрузились. Посмотрите логи с помощью `talosctl logs`. |
| Кластер существует, но новые изменения не применяются | Выполните `python3 00_destroy_vm.py` для полной очистки и затем `python3 run_all.py` заново. |
| `Permission denied` при работе с сокетом libvirt | Добавьте пользователя в группу `libvirt`: `sudo usermod -aG libvirt $USER` и перезайдите в систему. |

---

## 📄 Лицензия

Этот проект является частью более крупного репозитория `talos-terraform-argocd` и распространяется на условиях лицензии, указанной в корне репозитория.

### 🔗 Связанные ресурсы

- [Официальная документация Talos Linux](https://www.talos.dev)
- [Vagrant + libvirt руководство от Sidero Labs](https://www.siderolabs.com/docs/virtualized-platforms/vagrant-libvirt/)
- [Исходный код Talos Linux на GitHub](https://github.com/siderolabs/talos)
- [Основной репозиторий проекта](https://github.com/Viktor3434/talos-terraform-argocd)