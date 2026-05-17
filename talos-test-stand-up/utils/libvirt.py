# utils/libvirt.py
import re
import shutil
from pathlib import Path
from typing import List, Dict, Optional

from utils.cmd import run_cmd
from utils.ui import print_ok, print_fail, print_info, print_warn

# (импортируем сетевые параметры и конфигурацию пулов из config при необходимости)

def get_talos_vm_names() -> List[str]:
    """Список запущенных VM, чьё имя начинается с 'talos-'."""
    code, out, _ = run_cmd("virsh --connect qemu:///system list --name --state-running")
    if code != 0 or not out:
        print_fail("Не удалось получить список запущенных VMs")
        raise SystemExit(1)

    all_vms = [name.strip() for name in out.split('\n') if name.strip()]
    talos_vms = [vm for vm in all_vms if vm.startswith("talos-")]
    if not talos_vms:
        print_fail("Не найдено ни одной VM с именем talos-*")
        raise SystemExit(1)
    return talos_vms


def get_vm_ips(vm_names: List[str], network_name: str = "default") -> Dict[str, str]:
    """Словарь {имя_VM: IP} для списка имён."""
    ips = {}
    for vm in vm_names:
        # Попытка через domifaddr
        code, out, _ = run_cmd(f"virsh --connect qemu:///system domifaddr {vm} --source lease")
        if code == 0 and out:
            match = re.search(r"ipv4\s+(\d+\.\d+\.\d+\.\d+)/", out)
            if match:
                ips[vm] = match.group(1)
                continue
        # Запасной вариант — DHCP-лизы
        code, out, _ = run_cmd(f"virsh --connect qemu:///system net-dhcp-leases {network_name}")
        if code == 0:
            for line in out.split('\n'):
                if vm in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        ips[vm] = parts[4].split('/')[0]
                        break
        if vm not in ips:
            print_warn(f"Не удалось определить IP для {vm}")
    return ips


def get_vm_disk(vm_name: str) -> Optional[str]:
    """Имя первого диска VM (без CD-ROM/ISO). Например, 'vda'."""
    code, out, _ = run_cmd(f"virsh --connect qemu:///system domblklist {vm_name}")
    if code != 0 or not out:
        return None

    lines = out.splitlines()
    for line in lines[2:]:
        parts = line.split()
        if len(parts) < 2:
            continue
        target, source = parts[0], parts[1]
        if '.iso' in source.lower() or 'cdrom' in source.lower():
            continue
        return target
    return None


def get_install_disk(vm_name: str) -> str:
    """Возвращает /dev/имя_диска для установки Talos."""
    target = get_vm_disk(vm_name)
    if target is None:
        print_warn(f"Не удалось определить диск для {vm_name}, используем /dev/sda")
        return "/dev/sda"
    disk = f"/dev/{target}"
    print_ok(f"Определён установочный диск для {vm_name}: {disk}")
    return disk


# --- Работа с пулами и томами (используется в 00 и 01) ---

def pool_exists(name: str) -> bool:
    code, out, _ = run_cmd("virsh --connect qemu:///system pool-list --all --name")
    return name in out.split()


def pool_active(name: str) -> bool:
    code, out, _ = run_cmd(f"virsh --connect qemu:///system pool-info {name}")
    if code != 0:
        return False
    for line in out.split('\n'):
        if ("State:" in line and "running" in line) or ("Active:" in line and "yes" in line):
            return True
    return False


def volume_exists(pool_name: str, vol_name: str) -> bool:
    code, out, _ = run_cmd(f"virsh --connect qemu:///system vol-list {pool_name}")
    if code != 0:
        return False
    for line in out.splitlines():
        parts = line.split()
        if parts and parts[0] == vol_name:
            return True
    return False


def create_pool(name: str, target_path: Path) -> bool:
    target_path = Path(target_path).expanduser()
    target_path.mkdir(parents=True, exist_ok=True)
    cmd_def = f"virsh --connect qemu:///system pool-define-as {name} --type dir --target {target_path}"
    code, _, err = run_cmd(cmd_def)
    if code != 0:
        print_fail(f"Не удалось определить пул {name}: {err}")
        return False
    for sub_cmd in (f"pool-build {name}", f"pool-start {name}", f"pool-autostart {name}"):
        run_cmd(f"virsh --connect qemu:///system {sub_cmd}")
    return True


def delete_volume(pool_name: str, vol_name: str) -> bool:
    if not volume_exists(pool_name, vol_name):
        print_warn(f"Том {vol_name} не найден в пуле {pool_name}, пропускаем.")
        return True
    code, _, err = run_cmd(f"virsh --connect qemu:///system vol-delete --pool {pool_name} {vol_name}")
    if code == 0:
        print_ok(f"Том {vol_name} удалён из пула {pool_name}")
        return True
    else:
        print_fail(f"Не удалось удалить том {vol_name}: {err}")
        return False


def refresh_pool(name: str):
    run_cmd(f"virsh --connect qemu:///system pool-refresh {name}")