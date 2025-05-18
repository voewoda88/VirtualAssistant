import random

from vacore import VACore


def start(core: VACore):
    manifest = {
        "name": "Как дела",
        "version": "1.0",
        "require_online": False,

        "description": "Демонстрационный плагин\n"
                       "Голосовая команда: как дела|как твои дела|как ты",

        "commands": {
            "как дела|как твои дела|как ты": play_howareyou,
        }
    }
    return manifest


def play_howareyou(core: VACore, phrase: str):
    strs = [
        "У меня все отлично! Готова к работе.",
        "Все хорошо! Чем будем заниматься?"
    ]

    answer = random.choice(strs)
    core.play_voice_assistant_speech(answer)
