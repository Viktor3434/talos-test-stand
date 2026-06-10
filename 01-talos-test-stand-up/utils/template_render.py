from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import config

def generate_vagrantfile(template_dir: Path = None, output_path: Path = None):
    """Генерирует Vagrantfile из Jinja2 шаблона на основе config.py"""
    if template_dir is None:
        template_dir = Path(__file__).parent.parent  # или где лежит шаблон
    if output_path is None:
        output_path = config.VAGRANTFILE_DIR / "Vagrantfile"

    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("Vagrantfile.j2")

    # Передаем только нужные переменные из конфига
    context = {
        "iso_path": str(config.ISO_PATH),
        "pool_disks_name": config.POOL_DISKS_NAME,
        "control_planes_count": config.CONTROL_PLANES_COUNT,
        "workers_count": config.WORKERS_COUNT,

        "cp_memory": config.MEMORY_CP_NODES,
        "worker_memory": config.MEMORY_WORKER_NODES,
        "cp_cpus": config.CPU_CP_NODES,
        "worker_cpus": config.CPU_WORKER_NODES,
        
    }

    rendered = template.render(**context)
    output_path.write_text(rendered)
    print(f"✅ Vagrantfile сгенерирован: {output_path}")