#!/usr/bin/env python3
"""
Добавление Talos Linux worker-узлов в существующий кластер.
"""

import sys
from utils.ui import print_info, print_ok, print_fail, print_warn
from utils.libvirt import get_talos_vm_names, get_vm_ips
from utils.talos import apply_config, wait_for_workers_join
from config import WORKERS_COUNT, TALOS_CONF_DIR, TALOS_SECRET, KUBECONFIG

def check_required_files() -> None:
    required = [
        TALOS_SECRET,
        TALOS_CONF_DIR / "worker.yaml",
        TALOS_CONF_DIR / "talosconfig",
    ]
    missing = [f for f in required if not f.exists()]
    if missing:
        print_fail("Отсутствуют файлы конфигурации, сгенерируйте их с помощью install_masters.py:")
        for f in missing:
            print_fail(f"  - {f}")
        sys.exit(1)
    print_ok("Все необходимые файлы конфигурации найдены")

def get_worker_ips():
    """Возвращает IP-адреса worker-нод."""
    vm_names = get_talos_vm_names()
    ips = get_vm_ips(vm_names)
    workers = [ip for name, ip in ips.items() if "cp" not in name and "control" not in name]
    if not workers:
        print_fail("Не найдены worker-ноды")
        sys.exit(1)
    if len(workers) < WORKERS_COUNT:
        print_warn(f"Найдено воркеров: {len(workers)}, ожидалось: {WORKERS_COUNT}")
    else:
        print_ok(f"Найдено воркеров: {len(workers)}")
    return workers

def main():
    print_info("=== Добавление worker-узлов ===")
    check_required_files()
    worker_ips = get_worker_ips()

    apply_config(worker_ips, "worker.yaml")
    if KUBECONFIG.exists():
        wait_for_workers_join(KUBECONFIG, len(worker_ips))
    else:
        print_warn("kubeconfig не найден, пропускаем проверку присоединения.")

    print_ok("=== Worker-узлы добавлены ===")
    if KUBECONFIG.exists():
        print_info(f"Проверьте состояние: kubectl --kubeconfig {KUBECONFIG} get nodes")

if __name__ == "__main__":
    main()