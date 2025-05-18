import subprocess
import platform
from vacore import VACore


def start(core: VACore):
    manifest = {
        'name': 'Отключение, перезагрузка и спящий режим',
        'version': '1.1',
        'require_online': False,

        'commands': {
            'выключи компьютер|отключить питание|отключи питание|выключить компьютер|отключение|выключение': poweroff,
            'перезагрузи компьютер|перезагрузить компьютер|перезагрузка': reboot,
            'спящий режим|усыпи компьютер|перейди в спящий режим|сон|спи': sleep_mode,
        }
    }

    return manifest


def poweroff(core: VACore, phrase: str):
    try:
        core.play_voice_assistant_speech('Выполняю выключение компьютера')
        if platform.system() == "Windows":
            subprocess.Popen(["shutdown", "/s", "/t", "0"])
        else:
            subprocess.Popen(["poweroff"])
    except Exception:
        core.play_voice_assistant_speech("Ошибка при попытке выключения")


def reboot(core: VACore, phrase: str):
    try:
        core.play_voice_assistant_speech('Выполняю перезагрузку компьютера')
        if platform.system() == "Windows":
            subprocess.Popen(["shutdown", "/r", "/t", "0"])
        else:
            subprocess.Popen(["reboot"])
    except Exception:
        core.play_voice_assistant_speech("Ошибка при попытке перезагрузки")


def sleep_mode(core: VACore, phrase: str):
    try:
        core.play_voice_assistant_speech('Перевожу компьютер в спящий режим')
        system = platform.system()
        if system == "Windows":
            subprocess.Popen(["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"])
        elif system == "Linux":
            subprocess.Popen(["systemctl", "suspend"])
        else:
            core.play_voice_assistant_speech("Спящий режим не поддерживается на этой системе")
    except Exception:
        core.play_voice_assistant_speech("Ошибка при переходе в спящий режим")
