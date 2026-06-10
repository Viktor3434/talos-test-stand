#!/usr/bin/env python3
"""
Проверка зависимостей для кластера Talos + Vagrant + libvirt.
Создаёт/проверяет storage pool'ы, затем запускает vagrant up.
"""

import sys
import subprocess
from pathlib import Path

from config import (
    VAGRANTFILE_DIR, ISO_PATH, POOL_ISO_NAME, POOL_ISO_TARGET,
    POOL_DISKS_NAME, POOL_DISKS_TARGET, ISO_VOL_NAME,
    LIBVIRT_NETWORK, REQUIRED_GROUPS, DHCP_RANGE_START, DHCP_RANGE_END
)
from utils.ui import print_ok, print_fail, print_info, print_warn
from utils.checks import (
    check_command_exists, check_service_active, check_libvirt_network_active,
    check_user_in_groups, check_vagrant_plugin, check_iso_exists
)
from utils.libvirt import (
    pool_exists, pool_active, create_pool, volume_exists, refresh_pool
)
from utils.libvirt_network import configure_dhcp_range
from utils.template_render import generate_vagrantfile


def ensure_iso_pool() -> bool:
    """Убеждается, что пул ISO существует и в нём есть нужный том."""
    if not pool_exists(POOL_ISO_NAME):
        print_info(f"Пул {POOL_ISO_NAME} не найден. Создаём...")
        if not create_pool(POOL_ISO_NAME, POOL_ISO_TARGET):
            return False
    if not pool_active(POOL_ISO_NAME):
        print_info(f"Пул {POOL_ISO_NAME} не активен. Запускаем...")
        subprocess.run(f"virsh --connect qemu:///system pool-start {POOL_ISO_NAME}", shell=True)
    refresh_pool(POOL_ISO_NAME)
    if volume_exists(POOL_ISO_NAME, ISO_VOL_NAME):
        print_ok(f"Том {ISO_VOL_NAME} найден в пуле {POOL_ISO_NAME}")
        return True
    else:
        print_fail(f"Том {ISO_VOL_NAME} отсутствует в пуле {POOL_ISO_NAME}.")
        print_info(f"Убедитесь, что файл {ISO_PATH} лежит в {POOL_ISO_TARGET} и выполните:")
        print_info(f"  virsh --connect qemu:///system pool-refresh {POOL_ISO_NAME}")
        return False

def ensure_disks_pool() -> bool:
    """Убеждается, что пул для дисков существует и активен."""
    if not pool_exists(POOL_DISKS_NAME):
        print_info(f"Пул {POOL_DISKS_NAME} не найден. Создаём...")
        if not create_pool(POOL_DISKS_NAME, POOL_DISKS_TARGET):
            return False
    if not pool_active(POOL_DISKS_NAME):
        print_info(f"Пул {POOL_DISKS_NAME} не активен. Запускаем...")
        subprocess.run(f"virsh --connect qemu:///system pool-start {POOL_DISKS_NAME}", shell=True)
    refresh_pool(POOL_DISKS_NAME)
    print_ok(f"Пул {POOL_DISKS_NAME} готов.")
    return True

def main():
    print_info("Проверка зависимостей для стенда Talos + Vagrant + libvirt")
    all_ok = True

    # Проверка команд
    for cmd in ["vagrant", "virsh", "systemctl"]:
        if check_command_exists(cmd):
            print_ok(f"Команда '{cmd}' найдена")
        else:
            print_fail(f"Команда '{cmd}' не найдена")
            all_ok = False

    # Сервис libvirtd
    if check_service_active("libvirtd"):
        print_ok("Сервис libvirtd активен")
    else:
        print_fail("Сервис libvirtd не активен")
        all_ok = False

    # Сеть default
    if check_libvirt_network_active(LIBVIRT_NETWORK):
        print_ok(f"Сеть '{LIBVIRT_NETWORK}' активна")
    else:
        print_fail(f"Сеть '{LIBVIRT_NETWORK}' не активна")
        all_ok = False

    # Настройка DHCP-диапазона (если сеть активна)
    if all_ok:
        if not configure_dhcp_range(LIBVIRT_NETWORK, DHCP_RANGE_START, DHCP_RANGE_END):
            print_fail("Не удалось настроить DHCP-диапазон")
            all_ok = False

    # Группы пользователя
    if check_user_in_groups(REQUIRED_GROUPS):
        print_ok(f"Пользователь в группах: {', '.join(REQUIRED_GROUPS)}")
    else:
        print_fail(f"Пользователь не в группе {REQUIRED_GROUPS}")
        all_ok = False

    # Плагин vagrant-libvirt
    if check_vagrant_plugin():
        print_ok("Плагин vagrant-libvirt установлен")
    else:
        print_fail("Плагин vagrant-libvirt не установлен")
        all_ok = False

    # ISO-файл
    if check_iso_exists(ISO_PATH):
        print_ok(f"ISO-файл найден: {ISO_PATH}")
    else:
        print_fail(f"ISO-файл отсутствует: {ISO_PATH}")
        print_info(f"Скачайте: wget https://github.com/siderolabs/talos/releases/download/v1.13.0/metal-amd64.iso -O {ISO_PATH}")
        all_ok = False

    # Пул ISO и том
    if not ensure_iso_pool():
        all_ok = False

    # Пул дисков
    if not ensure_disks_pool():
        all_ok = False

    # Vagrantfile
    generate_vagrantfile()
    vagrantfile_path = VAGRANTFILE_DIR / "Vagrantfile"
    if vagrantfile_path.is_file():
        print_ok(f"Vagrantfile найден в {VAGRANTFILE_DIR}")
    else:
        print_fail("Vagrantfile не найден")
        all_ok = False

    # KVM
    if Path("/dev/kvm").exists():
        print_ok("/dev/kvm присутствует")
    else:
        print_warn("/dev/kvm отсутствует (KVM может быть недоступен)")

    if not all_ok:
        print_fail("Некоторые проверки не пройдены. Исправьте ошибки.")
        sys.exit(1)

    print_info("Все проверки пройдены. Запускаем vagrant up...")
    result = subprocess.run(["vagrant", "up"], cwd=VAGRANTFILE_DIR)
    if result.returncode != 0:
        print_fail("vagrant up завершился с ошибкой")
        sys.exit(1)
    print_ok("Кластер успешно запущен!")
    print_info("Тома в пуле pool-talos после запуска:")
    subprocess.run("virsh --connect qemu:///system vol-list pool-talos", shell=True)

if __name__ == "__main__":
    main()