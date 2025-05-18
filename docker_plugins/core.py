
from vacore import VACore

def start(core:VACore):
    manifest = {
        "name": "Core plugin",
        "version": "3.0",

        "default_options": {
            "mpcIsUse": True,
            "mpcHcPath": "C:\Program Files (x86)\K-Lite Codec Pack\MPC-HC64\mpc-hc64_nvo.exe",
            "mpcIsUseHttpRemote": False,

            "isOnline": False,
            "useTTSCache": False,
            "ttsEngineId": "silero_v3",
            "ttsEngineId2": "",
            "playWavEngineId": "consolewav",
            "linguaFrancaLang": "ru",
            "voiceAssNames": "ирина|ирины|ирину",
            "logPolicy": "cmd",

            "replyNoCommandFound": "Извини, я не поняла",
            "replyNoCommandFoundInContext": "Не поняла...",
            "replyOnlineRequired": "Для этой команды необходим онлайн",

            "contextDefaultDuration": 10,
            "contextRemoteWaitForCall": False,

            "tempDir": "temp",
            "fuzzyThreshold": 0.5,
        },

    }
    return manifest


def start_with_options(core: VACore, manifest: dict):
    options = manifest["options"]

    core.mpcHcPath = options["mpcHcPath"]
    core.mpcIsUse = options["mpcIsUse"]
    core.mpcIsUseHttpRemote = options["mpcIsUseHttpRemote"]
    core.isOnline = options["isOnline"]

    core.voiceAssNames = options["voiceAssNames"].split("|")
    core.ttsEngineId = options["ttsEngineId"]
    core.ttsEngineId2 = options["ttsEngineId2"]
    core.playWavEngineId = options["playWavEngineId"]
    core.logPolicy = options["logPolicy"]

    core.contextDefaultDuration = options["contextDefaultDuration"]
    core.contextRemoteWaitForCall = options["contextRemoteWaitForCall"]

    core.tmpdir = options["tempDir"]
    import os
    if not os.path.exists(core.tmpdir):
        os.mkdir(core.tmpdir)

    core.useTTSCache = options["useTTSCache"]
    core.tts_cache_dir = "tts_cache"
    if not os.path.exists(core.tts_cache_dir):
        os.mkdir(core.tts_cache_dir)
    if not os.path.exists(core.tts_cache_dir+"/"+core.ttsEngineId):
        os.mkdir(core.tts_cache_dir+"/"+core.ttsEngineId)

    import lingua_franca
    lingua_franca.load_language(options["linguaFrancaLang"])

    return manifest
