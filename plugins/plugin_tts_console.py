
import os

from vacore import VACore

modname = os.path.basename(__file__)[:-3]


def start(core: VACore):
    manifest = {
        "name": "TTS console (for debug)",
        "version": "1.0",
        "require_online": False,

        "tts": {
            "console": (init, say)
        }
    }
    return manifest


def init(core: VACore):
    pass


def say(core: VACore, text_to_speech: str):
    try:
        from termcolor import colored, cprint
        cprint("TTS: {}".format(text_to_speech),"blue")
    except Exception as e:
        print("TTS: {}".format(text_to_speech))