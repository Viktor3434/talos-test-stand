#!/usr/bin/env python3
"""Установка control plane."""
import sys
from utils.ui import print_info, print_ok, print_fail, print_warn
from utils.libvirt import get_talos_vm_names, get_vm_ips, get_install_disk
from utils.talos import (check_talosctl, generate_secret_if_missing, generate_config,
                         configure_talos_context, apply_config, wait_for_nodes_api,
                         bootstrap_cluster, fetch_kubeconfig)
from config import CONTROL_PLANES_COUNT, TALOS_CONF_DIR, REGISTRY_MIRRORS

def main():
    print_info("=== Установка Talos на master-узлы ===")
    check_talosctl()

    vm_names = get_talos_vm_names()
    ips = get_vm_ips(vm_names)

    # Выделяем мастер-IP и имена
    masters = {name: ip for name, ip in ips.items() if "cp" in name or "control" in name}
    if not masters:
        print_fail("Не найдены master-ноды")
        sys.exit(1)

    master_ips = list(masters.values())
    master_names = list(masters.keys())
    endpoint_ip = master_ips[0]

    install_disk = get_install_disk(master_names[0])

    generate_secret_if_missing()
    generate_config(endpoint_ip, install_disk, REGISTRY_MIRRORS)
    configure_talos_context(endpoint_ip)

    apply_config(master_ips, "controlplane.yaml")
    wait_for_nodes_api(master_ips, TALOS_CONF_DIR)
    bootstrap_cluster(endpoint_ip)
    kubeconfig = fetch_kubeconfig(endpoint_ip)

    print_ok("Control plane готов.")
    print_info(f"KUBECONFIG={kubeconfig}")

if __name__ == "__main__":
    main()