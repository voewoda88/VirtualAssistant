
from vacore import VACore

def start(core: VACore):
    manifest = {
        "name": "Подсказка по всем актуальным командам",
        "version": "1.0",
        "require_online": False,

        "commands": {
            "что|что умеешь|что можешь": help_start,
        }
    }
    return manifest


def help_start(core: VACore,
               phrase: str):
    core.say("Расказать кратко, подробно или отмена")
    core.context_set(menu_main)


def help_cancel(core: VACore, phrase: str):
    core.say("хорошо")
    return


def help_short(core: VACore, phrase: str):
    help_cmd(core, phrase, "short")
    return


def help_desc(core: VACore, phrase: str):
    help_cmd(core, phrase, "desc")
    return


menu_main = {"кратко|коротко|расскажи коротко|расскажи кратко|кратко пожалуйста|коротко пожалуйста": help_short,
             "подробно|расскажи подробно|расскажи подробнее|подробнее пожалуйста": help_desc, "отмена|отмени|отменить": help_cancel}


def help_cmd(core: VACore, phrase: str, mode_help: str):
    for manifs in core.plugin_manifests.keys():
        commands = core.plugin_manifests[manifs].get('commands')
        name = core.plugin_manifests[manifs].get('name')
        if commands != None:
            for keyall in commands.keys():
                keys = keyall.split("|")
                msg = keys[0]
                if msg == "что умеешь":
                    continue

                if mode_help == 'desc':
                    msg = msg + ' - ' + name

                print(msg)
                core.play_voice_assistant_speech(msg)

    return
