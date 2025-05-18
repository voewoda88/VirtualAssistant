import asyncio

from vacore import VACore
from websocket_creation import send_command


def start(core: VACore):
    manifest = {
        "name": "Яндекс музыка",
        "version": "1.0",
        "require_online": False,

        "commands": {
            "музыка": start_music,
            "волна": start_my_wave,
        }
    }

    return manifest


def start_music(core: VACore, phrase: str):
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(send_command("yandex_play_pause", ""))
    except RuntimeError:
        asyncio.run(send_command("yandex_play_pause", ""))


def start_my_wave(core, phrase: str):
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(send_command("yandex_music", ""))
    except RuntimeError:
        asyncio.run(send_command("yandex_music", ""))