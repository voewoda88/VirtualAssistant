
import os

from vacore import VACore
import pyttsx3

modname = os.path.basename(__file__)[:-3]


def start(core: VACore):
    manifest = {
        "name": "TTS pyttsx",
        "version": "1.1",
        "require_online": False,

        "description": """
TTS через pyttsx.
Обычно работает без проблем, если у вас Windows с русским языком; иначе лучше переставить engineId на vosk или silero_v3.
""",

        "default_options": {
            "sysId": 0,
        },

        "tts": {
            "pyttsx": (init,say,towavfile)
        }
    }
    return manifest


def start_with_options(core: VACore, manifest: dict):
    pass


def init(core: VACore):
    options = core.plugin_options(modname)

    core.ttsEngine = pyttsx3.init()

    """
    Установка голоса по умолчанию (индекс может меняться в зависимости от настроек операционной системы)
    """

    voices = core.ttsEngine.getProperty("voices")

    core.ttsEngine.setProperty("voice", voices[options["sysId"]].id)
    core.ttsEngine.setProperty("volume", 1.0)


def say(core: VACore, text_to_speech: str):
    """
    Проигрывание речи ответов голосового ассистента (без сохранения аудио)
    :param text_to_speech: текст, который нужно преобразовать в речь
    """
    core.ttsEngine.say(str(text_to_speech))
    core.ttsEngine.runAndWait()


def towavfile(core: VACore, text_to_speech: str, wavfile: str):
    """
    Проигрывание речи ответов голосового ассистента (без сохранения аудио)
    :param text_to_speech: текст, который нужно преобразовать в речь
    """
    core.ttsEngine.save_to_file(str(text_to_speech), wavfile)
    core.ttsEngine.runAndWait()