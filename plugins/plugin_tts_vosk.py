
import os

from vacore import VACore

modname = os.path.basename(__file__)[:-3]

# функция на старте
def start(core: VACore):
    manifest = {
        "name": "TTS vosk",
        "version": "1.3",
        "require_online": False,

        "description": "TTS через VOSK\n"
                       "ID для указания: vosk\n"
                       "Список голосов доступен здесь: https://giters.com/alphacep/vosk-tts",

        "default_options": {
            "modelId": "vosk-model-tts-ru-0.4-multi", # модель
            "speakerId": 0
        },

        "tts": {
            "vosk": (init, None, towavfile)
        }
    }
    return manifest


def start_with_options(core: VACore, manifest: dict):
    pass


def init(core: VACore):
    from vosk_tts.model import Model
    from vosk_tts.synth import Synth

    options = core.plugin_options(modname)

    core.ttsModel = Model(model_name = options['modelId'])
    core.ttsSynth = Synth(core.ttsModel)


def towavfile(core: VACore, text_to_speech: str,wavfile: str):
    """
    Проигрывание речи ответов голосового ассистента с сохранением в файл
    :param text_to_speech: текст, который нужно преобразовать в речь
    """
    options = core.plugin_options(modname)
    core.ttsSynth.synth(core.all_num_to_text(text_to_speech),wavfile,speaker_id=options['speakerId'])
