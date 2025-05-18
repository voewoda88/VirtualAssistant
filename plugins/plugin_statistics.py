import subprocess
import socket

from vacore import VACore


def start(core: VACore):
    manifest = {
        "name": "Информация о системе",
        "version": "1.1",
        "require_online": False,

        "commands": {
            "статистика|о системе|ресурсы|инфо": get_system_info,
        }
    }

    return manifest


def compute_suffix(value: str, variants: list):
    try:
        n = int(value.strip()[-1])
    except:
        n = 0
    if (n == 0) or (n >= 5):
        suffix = variants[0]
    elif n == 1:
        suffix = variants[1]
        if len(value) >= 2 and value.strip()[-2] == '1':
            suffix = variants[2]
    else:
        suffix = variants[2]
    return suffix


def get_values_from(data: str):
    tmp = data.split('/')
    first = tmp[0].replace("b'", "").strip()
    tmp = tmp[1].replace("%", "").split()
    second = tmp[0]
    third = tmp[1] if len(tmp) > 1 else "0"
    return first, second, third


def get_ip_address():
    try:
        # безопасный способ узнать IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "неизвестен"


def get_system_info(core: VACore, phrase: str):
    # IP
    ip = get_ip_address()
    core.play_voice_assistant_speech(f"АйПи адрес: {ip.replace('.', ' точка ')}")

    # CPU Load
    try:
        CPU = subprocess.check_output("top -bn1 | grep load | awk '{printf \"%.2f\", $(NF-2)}'", shell=True).decode()
        core.play_voice_assistant_speech(f"Загрузка процессора {CPU} процентов")
    except:
        core.play_voice_assistant_speech("Не удалось получить загрузку процессора")

    # Memory
    try:
        MemUsage = subprocess.check_output("free -m | awk 'NR==2{printf \"%s/%s %.2f%%\", $3,$2,$3*100/$2 }'", shell=True).decode()
        mem = get_values_from(MemUsage)
        percent = int(round(float(mem[2])))
        text = f"Свободно оперативной памяти {mem[0]} из {mem[1]} {compute_suffix(mem[1], ['мегабайтов', 'мегабайт', 'мегабайта'])}. "
        text += f"Что составляет {percent} {compute_suffix(str(percent), ['процентов', 'процент', 'процента'])} от доступного объема."
        core.play_voice_assistant_speech(text)
    except:
        core.play_voice_assistant_speech("Не удалось получить информацию о памяти")

    # Disk
    try:
        Disk = subprocess.check_output("df -h | awk '$NF==\"/\"{printf \"%d/%d %s\", $3,$2,$5}'", shell=True).decode()
        dsk = get_values_from(Disk)
        percent = int(dsk[2].replace('%', ''))
        text = f"Свободно на диске {dsk[0]} из {dsk[1]} {compute_suffix(dsk[1], ['гигабайтов', 'гигабайт', 'гигабайта'])}. "
        text += f"Что составляет {percent} {compute_suffix(str(percent), ['процентов', 'процент', 'процента'])} от общего объема."
        core.play_voice_assistant_speech(text)
    except:
        core.play_voice_assistant_speech("Не удалось получить информацию о диске")
