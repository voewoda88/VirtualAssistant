import os
import subprocess

from vacore import VACore

modname = os.path.basename(__file__)[:-3]


def start(core: VACore):
    manifest = {
        "name": "VScode",
        "version": "1.0",
        "require_online": False,

        "description": "Плагин для открытия Visual Studio Code\n",

        "options_label": {
            "Path": "Путь к приложению"
        },

        "default_options": {
            "Path": "",
        },

        "commands": {
            "открой вижлу|открой вс код|вс код|вижла|открой вижуал студио код|вижуал студио кодд": open_visual_studio,
        }
    }

    return manifest


def start_with_options(core: VACore, manifest: dict):
    pass


def open_visual_studio(core: VACore, phrase: str):
    options = core.plugin_options(modname)

    path = options["Path"]

    if not path or not os.path.exists(path):
        core.say("Путь к вижуал студио код не указан или файл не найден.")

    try:
        subprocess.Popen([path])
        core.say("Открываю вижуал студио код.")
    except Exception as e:
        core.say("Ошибка запуска вижуал студио код.")
        print(e)
