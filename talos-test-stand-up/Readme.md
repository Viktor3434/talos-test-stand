Talos Linux Test Stand
======================
Автоматизированное развёртывание тестового кластера Talos Linux на виртуальных машинах с использованием Vagrant + libvirt.

В данный момент проект представляет собой набор Python-скриптов, разбитых по этапам: проверка зависимостей, создание виртуальных машин, установка control plane и добавление worker-узлов. Вся логика вынесена в переиспользуемые модули, а управляющий скрипт run_all.py позволяет выполнить полный цикл одной командой.

> Важно: Стенд предназначен для разработки и тестирования. Не используйте конфигурацию как есть в production-средах.

**Требования** 
- ОС: Linux с установленным KVM и libvirt.
- Vagrant (рекомендуется версия 2.2+) и плагин vagrant-libvirt.
- Python 3.7+ с модулями стандартной библиотеки (никаких дополнительных пакетов не требуется).
- talosctl – CLI для управления Talos ([инструкция по установке](https://www.talos.dev/docs/v1.9/introduction/getting-started/#talosctl)).
- kubectl (опционально, для проверки кластера).
- ISO-образ Talos metal-amd64.iso (см. ниже).

# Установка и настройка
1. Клонирование репозитория
bash
git clone <репозиторий> talos-terraform-argocd
cd talos-terraform-argocd
2. Установка зависимостей для Vagrant
```bash
# Установите Vagrant согласно документации вашего дистрибутива
# Добавьте плагин libvirt
vagrant plugin install vagrant-libvirt

# Убедитесь, что пользователь состоит в группах libvirt и kvm
sudo usermod -aG libvirt,kvm $USER
newgrp libvirt
```
3. Установка talosctl
Скачайте бинарник с GitHub и поместите в `$PATH`:

```bash
curl -Lo /usr/local/bin/talosctl https://github.com/siderolabs/talos/releases/latest/download/talosctl-$(uname -s | tr '[:upper:]' '[:lower:]')-amd64
chmod +x /usr/local/bin/talosctl
```
4. Скачивание ISO-образа
Поместите файл *metal-amd64.iso* в ~/ISO-images/ (путь по умолчанию в config.py):
```bash
mkdir -p ~/ISO-images
wget -O ~/ISO-images/metal-amd64.iso https://github.com/siderolabs/talos/releases/download/v1.13.0/metal-amd64.iso
```
5. Конфигурация (опционально) \
Все настройки находятся в config.py. Вы можете изменить количество узлов, имена пулов, пути. Важно, чтобы конфигурация соответствовала вашему Vagrantfile.

# Структура проекта
```
.
├── 00_destroy_vm.py               # Уничтожение стенда (vagrant destroy + удаление дисков)
├── 01_check_and_vagrant_up.py     # Проверка всех зависимостей и запуск vagrant up
├── 02_install_masters.py          # Установка Talos на control plane узлы
├── 03_install_workers.py          # Добавление worker-узлов в кластер
├── run_all.py                     # Оркестратор: последовательный запуск всех шагов
├── config.py                      # Общие константы и настройки
├── Vagrantfile                    # Описание виртуальных машин для Vagrant
└── utils/                         # Модули с общими функциями
    ├── __init__.py
    ├── cmd.py                     # Запуск shell-команд
    ├── ui.py                      # Цветной вывод сообщений
    ├── libvirt.py                 # Работа с libvirt (пулы, тома, IP-адреса)
    ├── checks.py                  # Проверки окружения (сервисы, плагины, группы)
    └── talos.py                   # Взаимодействие с Talos (генерация конфигов, bootstrap)
```

# Быстрый старт
После настройки окружения запустите оркестратор из корня проекта:

```bash
python3 run_all.py
```
Скрипт выполнит следующие шаги:
1. Проверит все зависимости и запустит vagrant up.
2. Дождётся получения IP-адресов виртуальными машинами.
3. Установит Talos на control plane и инициализирует кластер.
4. Добавит worker-узлы.

В результате вы получите работающий кластер и файлы конфигурации в ~/.talos/:
- talosconfig – конфигурация для talosctl
- kubeconfig – конфигурация для kubectl

Пример проверки кластера после завершения:
```bash
export KUBECONFIG=~/.talos/kubeconfig
kubectl get nodes
```
# Пошаговое использование
Если требуется выполнить шаги вручную (например, для отладки), вы можете запускать скрипты по отдельности.

0. Уничтожение предыдущего стенда (опционально).\
Удаляет все виртуальные машины через Vagrant и очищает дисковые тома в пуле pool-talos.

```bash
python3 00_destroy_vm.py
```

1. Проверка и создание VM.\
Проверяет наличие команд, активность libvirtd, сеть, права пользователя, плагин Vagrant, наличие ISO-образа в пуле, и затем выполняет vagrant up.

```bash
python3 01_check_and_vagrant_up.py
```

2. Установка control plane.\
Определяет IP-адреса мастер-нод (имя содержит cp).\
Генерирует secrets.yaml и конфигурации Talos.\
Настраивает talosconfig.\
Применяет controlplane.yaml к каждому мастеру.\
Ожидает перезагрузки узлов и выполняет bootstrap.\
Получает kubeconfig.
```bash
python3 02_install_masters.py
```

3. Добавление worker-узлов.\
Находит IP-адреса узлов, не содержащих cp в имени.\
Применяет к ним worker.yaml.\
Ожидает их появления в кластере (Ready).
```bash
python3 03_install_workers.py
```
## Конфигурация (config.py)
| Параметр               | Значение по умолчанию            | Описание                                                     |
|------------------------|----------------------------------|--------------------------------------------------------------|
| `CLUSTER_NAME`         | `"talos-cluster"`                | Имя кластера Talos                                           |
| `NETWORK_NAME`         | `"default"`                      | Имя виртуальной сети libvirt                                 |
| `CONTROL_PLANES_COUNT` | `1`                              | Ожидаемое количество master-нод                              |
| `WORKERS_COUNT`        | `2`                              | Ожидаемое количество worker-нод                              |
| `TALOS_CONF_DIR`       | `~/.talos`                       | Каталог для хранения `secrets.yaml`, конфигов и `kubeconfig` |
| `ISO_PATH`             | `~/ISO-images/metal-amd64.iso`   | Путь к ISO-образу Talos                                      |
| `POOL_ISO_NAME`        | `"pool"`                         | Имя libvirt-пула для ISO-образов                             |
| `POOL_ISO_TARGET`      | `~/ISO-images`                   | Путь к директории пула ISO на хост-машине                    |
| `POOL_DISKS_NAME`      | `"pool-talos"`                   | Имя libvirt-пула для дисков виртуальных машин                |
| `POOL_DISKS_TARGET`    | `~/VirtualMachines/TalOS-linux`  | Путь к директории пула дисков на хост-машине                 |
| `ISO_VOL_NAME`         | `"metal-amd64.iso"`              | Имя тома с ISO-образом в пуле                                |
| `LIBVIRT_NETWORK`      | `"default"`                      | Виртуальная сеть для DHCP (алиас для `NETWORK_NAME`)         |
| `REQUIRED_GROUPS`      | `["libvirt"]`                    | Группы, в которых должен состоять пользователь               |
Измените значения в config.py в соответствии с вашим окружением и Vagrantfile.