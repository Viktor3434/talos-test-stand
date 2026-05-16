# config.py
from pathlib import Path

# --- Имена и подсети ---
CLUSTER_NAME = "talos-cluster"
NETWORK_NAME = "default"

# --- Количество узлов ---
CONTROL_PLANES_COUNT = 1
WORKERS_COUNT = 2

# --- Пути ---
TALOS_CONF_DIR = Path("~/.talos").expanduser()
TALOS_SECRET = TALOS_CONF_DIR / "secrets.yaml"
KUBECONFIG = TALOS_CONF_DIR / "kubeconfig"

# --- Vagrant и libvirt ---
VAGRANTFILE_DIR = Path.cwd()  # предполагается, что запуск из директории с Vagrantfile
LIBVIRT_NETWORK = "default"
REQUIRED_GROUPS = ["libvirt"]
ISO_PATH = Path("~/ISO-images/metal-amd64.iso").expanduser()
POOL_ISO_NAME = "pool"
POOL_ISO_TARGET = Path("~/ISO-images").expanduser()
POOL_DISKS_NAME = "pool-talos"
POOL_DISKS_TARGET = Path("~/VirtualMachines/TalOS-linux").expanduser()
ISO_VOL_NAME = "metal-amd64.iso"


# --- Ожидаемые имена дисков (формируются из количества узлов) ---
EXPECTED_DISK_VOLS = (
    [f"talos-cp-{i}.qcow2" for i in range(1, CONTROL_PLANES_COUNT + 1)] +
    [f"talos-worker-{i}.qcow2" for i in range(1, WORKERS_COUNT + 1)]
)