import re
from utils.cmd import run_cmd
from utils.ui import print_ok, print_info, print_warn, print_fail

def configure_dhcp_range(network: str, start_ip: str, end_ip: str) -> bool:
    """
    Настраивает DHCP-диапазон виртуальной сети libvirt.
    Удаляет все существующие диапазоны и добавляет один новый [start_ip, end_ip].
    Возвращает True, если изменения не потребовались или успешно применены.
    """
    # Получаем XML сети для анализа
    code, xml, err = run_cmd(f"virsh --connect qemu:///system net-dumpxml {network}")
    if code != 0:
        print_fail(f"Не удалось получить конфигурацию сети {network}: {err}")
        return False

    # Ищем все <range start="..." end="..."/> с помощью регулярки
    ranges = re.findall(r'<range\s+start=[\'"]([^\'"]+)[\'"]\s+end=[\'"]([^\'"]+)[\'"]\s*/>', xml)

    desired_range_xml = f'<range start="{start_ip}" end="{end_ip}"/>'
    need_update = True

    if ranges:
        # Проверяем, совпадает ли первый (или единственный) диапазон с нужным
        if len(ranges) == 1 and ranges[0] == (start_ip, end_ip):
            print_ok(f"DHCP-диапазон сети {network} уже настроен: {start_ip} - {end_ip}")
            return True
        # Удаляем все существующие диапазоны
        for s, e in ranges:
            del_xml = f'<range start="{s}" end="{e}"/>'
            code, _, err = run_cmd(
                f"virsh --connect qemu:///system net-update {network} delete ip-dhcp-range '{del_xml}' --live --config"
            )
            if code != 0:
                print_warn(f"Не удалось удалить старый диапазон {s}-{e}: {err}")
                # Продолжаем, возможно, его уже нет
    # Добавляем новый диапазон
    code, _, err = run_cmd(
        f"virsh --connect qemu:///system net-update {network} add ip-dhcp-range '{desired_range_xml}' --live --config"
    )
    if code != 0:
        print_fail(f"Не удалось добавить новый DHCP-диапазон: {err}")
        return False

    print_ok(f"DHCP-диапазон сети {network} установлен: {start_ip} - {end_ip}")
    return True