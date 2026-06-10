# utils/checks.py
import os
import shutil
from pathlib import Path
from utils.cmd import run_cmd

def check_command_exists(cmd: str) -> bool:
    """Проверяет, доступна ли команда в $PATH."""
    return shutil.which(cmd) is not None

def check_service_active(service: str) -> bool:
    """Проверяет, активен ли systemd-сервис."""
    code, out, _ = run_cmd(f"systemctl is-active {service}")
    return code == 0 and out == "active"

def check_libvirt_network_active(network: str) -> bool:
    """Проверяет, активна ли виртуальная сеть libvirt."""
    code, out, _ = run_cmd(f"virsh --connect qemu:///system net-info {network}")
    if code != 0:
        return False
    for line in out.split('\n'):
        if "Active:" in line and "yes" in line:
            return True
    return False

def check_user_in_groups(groups: list) -> bool:
    """Проверяет, состоит ли текущий пользователь во всех указанных группах."""
    user = os.getenv("USER")
    if not user:
        return False
    code, out, _ = run_cmd("groups")
    if code != 0:
        return False
    user_groups = out.split()
    return all(grp in user_groups for grp in groups)

def check_vagrant_plugin(plugin_name: str = "vagrant-libvirt") -> bool:
    """Проверяет, установлен ли указанный плагин Vagrant."""
    code, out, _ = run_cmd("vagrant plugin list")
    return code == 0 and plugin_name in out

def check_iso_exists(path: Path) -> bool:
    """Проверяет, существует ли ISO-файл по заданному пути."""
    return Path(path).is_file()