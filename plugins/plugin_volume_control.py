# Управление громкостью через pycaw
# author: Oleg Bakharev (переписано с использованием pycaw)

from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL, CoInitialize
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from vacore import VACore


def start(core: VACore):
    CoInitialize()
    manifest = {
        "name": "Управление громкостью через pycaw",
        "version": "2.0",
        "require_online": False,

        "commands": {
            "без звука|выключи звук|заглушить звук|выключить звук|убрать звук|тишина": mute_volume,
            "восстановить звук|включи звук|включить звук|верни звук|конец тишине": unmute_volume,
            "тише|уменьши громкость|уменьшить громкость|понизить громкость": lower_volume,
            "громче|увеличь громкость|увеличить громкость|повысить громкость": raise_volume,
            "полная громкость|звук на максимум|максимальная громкость": full_volume,
            "минимальный звук|минимум звука|звук на минимум|минимальная громкость": min_volume,
        }
    }

    return manifest


def get_volume_interface():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))


def mute_volume(core: VACore, phrase: str):
    get_volume_interface().SetMute(1, None)


def unmute_volume(core: VACore, phrase: str):
    get_volume_interface().SetMute(0, None)


def lower_volume(core: VACore, phrase: str):
    vol = get_volume_interface()
    current = vol.GetMasterVolumeLevelScalar()
    vol.SetMasterVolumeLevelScalar(max(0.0, current - 0.05), None)


def raise_volume(core: VACore, phrase: str):
    vol = get_volume_interface()
    current = vol.GetMasterVolumeLevelScalar()
    vol.SetMasterVolumeLevelScalar(min(1.0, current + 0.05), None)


def full_volume(core: VACore, phrase: str):
    get_volume_interface().SetMasterVolumeLevelScalar(1.0, None)


def min_volume(core: VACore, phrase: str):
    get_volume_interface().SetMasterVolumeLevelScalar(0.1, None)
