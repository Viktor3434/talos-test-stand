# utils/cmd.py
import subprocess
from typing import Tuple, Optional

def run_cmd(cmd: str, capture_output=True, check=False,
            timeout: Optional[int] = None, env: Optional[dict] = None) -> Tuple[int, str, str]:
    """
    Универсальная функция запуска shell-команды.
    Возвращает (returncode, stdout, stderr).
    """
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=capture_output, text=True,
            timeout=timeout, env=env
        )
        if capture_output:
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        return result.returncode, "", ""
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)