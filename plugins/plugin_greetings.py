import random
from vacore import VACore


def start(core: VACore):
    manifest = {
        "name": "Привет",
        "version": "1.0",
        "require_online": False,

        "description": "Демонстрационный плагин\n"
                       "Голосовая команда: привет|доброе утро",

        "commands": {
            "привет|доброе утро|добрый день|здравствуй": play_greetings,
        }
    }
    return manifest


def play_greetings(core: VACore, phrase: str):
    greetings = [
        "И тебе привет!",
        "Рада тебя видеть!",
    ]
    greet_str = greetings[random.randint(0, len(greetings) - 1)]
    print(f"- Сейчас я скажу фразу {greet_str}...\nЕсли вы её не услышите, значит, у вас проблемы с TTS или выводом звука и их надо настроить через менеджер настроек.")
    core.play_voice_assistant_speech(greet_str)
    print(f"- Я сказала фразу {greet_str}")


