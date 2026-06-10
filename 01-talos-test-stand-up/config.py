# config.py
from pathlib import Path

# --- Имена и подсети ---
CLUSTER_NAME = "talos-cluster"
NETWORK_NAME = "default"

# --- Количество узлов ---
CONTROL_PLANES_COUNT = 1
WORKERS_COUNT = 1

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

MEMORY_CP_NODES = 6144
MEMORY_WORKER_NODES = 8192
CPU_CP_NODES = 2
CPU_WORKER_NODES = 6

# For MetalLB
DHCP_RANGE_START = "192.168.122.2"
DHCP_RANGE_END = "192.168.122.100"

# --- Ожидаемые имена дисков (формируются из количества узлов) ---
EXPECTED_DISK_VOLS = (
    [f"talos-cp-{i}.qcow2" for i in range(1, CONTROL_PLANES_COUNT + 1)] +
    [f"talos-worker-{i}.qcow2" for i in range(1, WORKERS_COUNT + 1)]
)

# ---- Registry mirrors (необязательно) ----
# REGISTRY_MIRRORS = {}   # оставьте пустым, если зеркала не нужны
# Если словарь не пустой, будет сгенерирован патч для --config-patch
REGISTRY_MIRRORS = {
    "registry.k8s.io": {
        "endpoints": [
            "https://k8s.kubesre.xyz",
            "https://registry-k8s-io.mirrors.sjtug.sjtu.edu.cn",
            "https://k8s.nju.edu.cn"
            # "https://k8s.m.daocloud.io",
        ]
    },
    # "docker.io": {
    #     "endpoints": ["https://mirror.example.com"]
    # }
}