import platform

from vacore import VACore


def start(core: VACore):
    manifest = {
        "name": "Температура Ирины",
        "version": "1.0",
        "require_online": False,

        "commands": {
            "твоя температура|температура|температура процессора|нагрев|какая температура|какая у тебя температура|температура компьютера": get_temperature,
        }
    }

    return manifest


def compute_suffix(value: str, variants: list):
    n = int(value.strip()[-1])
    if (n == 0) or (n >= 5):
        suffix = variants[0]
    elif (n == 1):
        suffix = variants[1]
        if len(value) >= 2:
            if value.strip()[-2] == '1':
                suffix = variants[2]
    else:
        suffix = variants[2]
    return suffix


def get_temperature(core: VACore, phrase: str):
    system = platform.system()

    temperature = None

    if system == "Linux":
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temperature = float(f.read()) / 1000
        except Exception as e:
            core.play_voice_assistant_speech("Не удалось получить температуру на Linux.")
            print("Ошибка:", e)
            return

    elif system == "Windows":
        try:
            import wmi
            w = wmi.WMI(namespace="root\\wmi")
            temperature_info = w.MSAcpi_ThermalZoneTemperature()
            if temperature_info:
                temp_raw = temperature_info[0].CurrentTemperature
                temperature = (temp_raw / 10.0) - 273.15
        except Exception as e:
            core.play_voice_assistant_speech("Не удалось получить температуру на Windows.")
            print("Ошибка:", e)
            return

    if temperature is not None:
        temp_rounded = round(temperature)
        text = f"Моя температура {temp_rounded} {compute_suffix(str(temp_rounded), ['градусов', 'градус', 'градуса'])}"
        core.play_voice_assistant_speech(text)
    else:
        core.play_voice_assistant_speech("Температура неизвестна.")