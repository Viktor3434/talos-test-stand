# utils/ui.py
def print_ok(msg: str):    print(f"\033[92m✓ {msg}\033[0m")
def print_fail(msg: str):  print(f"\033[91m✗ {msg}\033[0m")
def print_info(msg: str):  print(f"\033[94mℹ {msg}\033[0m")
def print_warn(msg: str):  print(f"\033[93m⚠ {msg}\033[0m")