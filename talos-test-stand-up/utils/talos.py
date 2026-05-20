# utils/talos.py
import time
import os
import json
from pathlib import Path
from typing import List

from utils.cmd import run_cmd
from utils.ui import print_ok, print_fail, print_info, print_warn
from config import CLUSTER_NAME, TALOS_CONF_DIR, TALOS_SECRET

def check_talosctl() -> None:
    code, _, _ = run_cmd("which talosctl")
    if code != 0:
        print_fail("talosctl не найден. Установите: https://www.talos.dev/...")
        raise SystemExit(1)
    print_ok("talosctl найден")


def generate_secret_if_missing() -> None:
    TALOS_CONF_DIR.mkdir(parents=True, exist_ok=True)
    if TALOS_SECRET.exists():
        print_ok(f"secrets.yaml уже существует: {TALOS_SECRET}")
        return
    print_info("Генерация secrets.yaml...")
    code, _, err = run_cmd(f"talosctl gen secrets --output-file {TALOS_SECRET}")
    if code != 0:
        print_fail(f"Ошибка генерации secrets: {err}")
        raise SystemExit(1)
    print_ok("secrets.yaml создан")


def generate_config(endpoint_ip: str, install_disk: str,
                    registry_mirrors: Optional[dict] = None) -> None:

    print_info(f"Генерация конфигураций для {CLUSTER_NAME} "
               f"с endpoint https://{endpoint_ip}:6443")

    cmd = (
        f"talosctl gen config {CLUSTER_NAME} https://{endpoint_ip}:6443 "
        f"--with-secrets {TALOS_SECRET} "
        f"-o {TALOS_CONF_DIR} "
        f"--install-disk {install_disk} "
        f"--force"
    )

    if registry_mirrors:
        patch = {
            "machine": {
                "registries": {
                    "mirrors": registry_mirrors
                }
            }
        }
        # Запись во временный файл
        patch_file = TALOS_CONF_DIR / ".mirrors_patch.json"
        patch_file.write_text(json.dumps(patch))
        cmd += f" --config-patch @{patch_file}"
        print_info(f"Добавлены registry mirrors (через файл патча {patch_file})")

    code, _, err = run_cmd(cmd)
    if code != 0:
        print_fail(f"Ошибка генерации конфигов: {err}")
        raise SystemExit(1)

    # Сохраняем параметры кластера
    params = {
        "cluster_name": CLUSTER_NAME,
        "endpoint": f"https://{endpoint_ip}:6443",
        "install_disk": install_disk
    }
    (TALOS_CONF_DIR / ".cluster_params.json").write_text(json.dumps(params, indent=2))
    print_ok("Конфигурации сгенерированы")


def configure_talos_context(endpoint_ip: str) -> None:
    talosconfig = TALOS_CONF_DIR / "talosconfig"
    if not talosconfig.exists():
        print_fail("talosconfig не найден — невозможно настроить контекст")
        raise SystemExit(1)
    print_info("Настройка talosconfig: установка контекста и endpoint...")
    for cmd_part, desc in [
        (f"talosctl --talosconfig={talosconfig} config context {CLUSTER_NAME}", "контекст"),
        (f"talosctl --talosconfig={talosconfig} config endpoint {endpoint_ip}", "endpoint"),
    ]:
        code, _, err = run_cmd(cmd_part)
        if code != 0:
            print_warn(f"Не удалось установить {desc}: {err}")
        else:
            print_ok(f"{desc.capitalize()} установлен: {CLUSTER_NAME if 'контекст' in desc else endpoint_ip}")


def apply_config(ips: List[str], config_file: str, config_dir: Path = TALOS_CONF_DIR) -> None:
    filepath = config_dir / config_file
    for ip in ips:
        print_info(f"  Применение {config_file} к {ip}")
        code, _, err = run_cmd(
            f"talosctl apply-config --insecure --nodes {ip} --file {filepath}"
        )
        if code != 0:
            print_fail(f"  Ошибка на {ip}: {err}")
            raise SystemExit(1)
        print_ok(f"  Конфигурация применена к {ip}")


def wait_for_talos_api(ip: str, insecure: bool, timeout: int = 120, env=None) -> bool:
    start = time.time()
    cmd = f"talosctl version --nodes {ip}"
    if insecure:
        cmd += " --insecure"
    while time.time() - start < timeout:
        code, _, _ = run_cmd(cmd, timeout=5, env=env)
        if code == 0:
            return True
        time.sleep(5)
    return False


def wait_for_nodes_api(ips: List[str], config_dir: Path, timeout: int = 120) -> None:
    env = os.environ.copy()
    env["TALOSCONFIG"] = str(config_dir / "talosconfig")
    print_info("Ожидание доступности Talos API...")
    for ip in ips:
        print_info(f"  Ожидание {ip}...")
        if not wait_for_talos_api(ip, insecure=True, timeout=timeout, env=env):
            print_warn(f"  Таймаут ожидания {ip} в insecure-режиме")
        if not wait_for_talos_api(ip, insecure=False, timeout=30, env=env):
            print_warn(f"  Не удалось подключиться к {ip} с talosconfig")
        else:
            print_ok(f"  API Talos на {ip} доступен")


def bootstrap_cluster(endpoint_ip: str, config_dir: Path = TALOS_CONF_DIR) -> None:
    print_info(f"Bootstrap на {endpoint_ip}...")
    for attempt in range(2):
        code, _, err = run_cmd(
            f"talosctl bootstrap --nodes {endpoint_ip} --talosconfig={config_dir}/talosconfig"
        )
        if code == 0:
            print_ok("Bootstrap завершён")
            return
        if attempt == 0:
            print_warn(f"Ошибка: {err}, повтор через 10 сек...")
            time.sleep(10)
    print_fail(f"Ошибка bootstrap: {err}")
    raise SystemExit(1)


def fetch_kubeconfig(endpoint_ip: str, config_dir: Path = TALOS_CONF_DIR) -> Path:
    env = os.environ.copy()
    env["TALOSCONFIG"] = str(config_dir / "talosconfig")
    print_info("Получение kubeconfig...")
    code, _, err = run_cmd(f"talosctl kubeconfig {config_dir} --nodes {endpoint_ip}", env=env)
    if code != 0:
        print_fail(f"Ошибка получения kubeconfig: {err}")
        raise SystemExit(1)
    kubeconfig_path = config_dir / "kubeconfig"
    print_ok(f"kubeconfig сохранён в {kubeconfig_path}")
    return kubeconfig_path


def wait_for_workers_join(kubeconfig: Path, expected_count: int, timeout: int = 180) -> bool:
    env = os.environ.copy()
    env["KUBECONFIG"] = str(kubeconfig)
    print_info(f"Ожидание {expected_count} worker-нод (до {timeout} сек)...")
    start = time.time()
    while time.time() - start < timeout:
        code, out, _ = run_cmd("kubectl get nodes --no-headers", env=env)
        if code == 0:
            lines = out.split('\n') if out else []
            worker_lines = [l for l in lines if 'control-plane' not in l and l.strip()]
            if len(worker_lines) >= expected_count:
                print_ok(f"Все {expected_count} worker-нод присоединились")
                return True
        time.sleep(10)
    print_warn("Таймаут ожидания worker-нод")
    return False