#!/usr/bin/env python3
"""
Оркестратор развёртывания кластера Talos.
Последовательно запускает скрипты, с ожиданием готовности VM после vagrant up.
"""

import subprocess
import sys
import time

from utils.ui import print_info, print_ok, print_fail, print_warn
from utils.libvirt import get_talos_vm_names, get_vm_ips

# Максимальное время ожидания (сек) для получения IP всеми VM
VM_READY_TIMEOUT = 180
# Интервал опроса (сек)
POLL_INTERVAL = 10

SCRIPTS = [
    "01_check_and_vagrant_up.py",
    "02_install_masters.py",
    "03_install_workers.py",
]

def wait_for_all_vm_ips(timeout: int = VM_READY_TIMEOUT, interval: int = POLL_INTERVAL):
    """Ожидает, пока все talos-* VM не получат IP-адреса."""
    print_info("Ожидание получения IP-адресов всеми виртуальными машинами...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            vm_names = get_talos_vm_names()
            ips = get_vm_ips(vm_names)
        except SystemExit:
            # Если функция аварийно завершает (например, нет VM), пробуем позже
            print_warn("Пока не удалось получить список VM, повтор...")
            time.sleep(interval)
            continue

        missing = [vm for vm in vm_names if vm not in ips]
        if not missing:
            print_ok(f"Все {len(vm_names)} VM получили IP:")
            for vm, ip in ips.items():
                print_info(f"  {vm}: {ip}")
            return True
        else:
            print_info(f"Ждём IP для {len(missing)} VM (из {len(vm_names)}). Следующая проверка через {interval} сек...")
            time.sleep(interval)

    print_fail(f"Таймаут ({timeout} сек): не все VM получили IP.")
    return False

def main():
    for script in SCRIPTS:
        print(f"--- Запуск {script} ---")
        result = subprocess.run([sys.executable, script], check=False)
        if result.returncode != 0:
            print_fail(f"Скрипт {script} завершился с ошибкой, остановка.")
            sys.exit(1)
        # После успешного завершения 01_check_and_vagrant_up.py ждём IP
        if script == "01_check_and_vagrant_up.py":
            if not wait_for_all_vm_ips():
                print_fail("Не удалось дождаться готовности VM. Прерываем развёртывание.")
                sys.exit(1)
            print_ok("Виртуальные машины готовы, продолжаем...")

    print_ok("Все шаги выполнены успешно.")

if __name__ == "__main__":
    main()