#!/usr/bin/env python3
"""Уничтожение стенда."""
import sys
import subprocess
from pathlib import Path

from utils.ui import print_info, print_ok, print_fail
from utils.libvirt import delete_volume, refresh_pool, pool_exists
from utils.checks import check_command_exists
from config import VAGRANTFILE_DIR, POOL_DISKS_NAME, EXPECTED_DISK_VOLS


def main():
    print_info("Уничтожение стенда Talos + Vagrant + libvirt")
    # проверки и удаление, используя импортированные функции
    # ...
    # vagrant destroy
    if not (VAGRANTFILE_DIR / "Vagrantfile").exists():
        print_fail("Vagrantfile не найден")
        sys.exit(1)
    subprocess.run(["vagrant", "destroy", "-f"], cwd=VAGRANTFILE_DIR)
    # удаление томов
    for vol in EXPECTED_DISK_VOLS:
        delete_volume(POOL_DISKS_NAME, vol)
    refresh_pool(POOL_DISKS_NAME)
    print_ok("Стенд уничтожен.")

if __name__ == "__main__":
    main()