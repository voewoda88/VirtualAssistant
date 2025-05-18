
import time
import os

from vacore import VACore
import utils.num_to_text_ru as num_to_text

female_units_min2 = ((u'минуту', u'минуты', u'минут'), 'f')
female_units_min = ((u'минута', u'минуты', u'минут'), 'f')
female_units_sec2 = ((u'секунду', u'секунды', u'секунд'), 'f')
female_units_sec = ((u'секунда', u'секунды', u'секунд'), 'f')

modname = os.path.basename(__file__)[:-3]

def start(core: VACore):
    manifest = {
        "name": "Таймер",
        "version": "1.2",
        "require_online": False,

        "description": "Плагин таймера\n"
                       "Голосовая команда: таймер, таймер десять минут, таймер двадцать секунд\n"
                        "Просто 'таймер' ставит таймер на 5 минут",

        "options_label": {
            "wavRepeatTimes": "число повторений WAV-файла сигнала таймера",
            "wavPath": "путь к звуковому файлу",
        },

        "default_options": {
            "wavRepeatTimes": 1,
            "wavPath": 'media/timer.wav',
        },

        "commands": {
            "поставь таймер|поставь тайгер|таймер|тайгер": set_timer,
        }
    }
    return manifest


def start_with_options(core: VACore, manifest: dict):
    pass


def set_timer(core: VACore, phrase: str):
    if phrase == "":
        txt = num_to_text.num2text(5, female_units_min)
        set_timer_real(core, 5*60, txt)
        return

    phrase += " "

    if(phrase.startswith("на ")):
        phrase = phrase[3:]

    for i in range(100, 1, -1):
        txt = num_to_text.num2text(i, female_units_sec) + " "
        if phrase.startswith(txt):
            set_timer_real(core, i, txt)
            return

        txt2 = num_to_text.num2text(i, female_units_sec2) + " "
        if phrase.startswith(txt2):
            set_timer_real(core, i, txt)
            return

        txt3 = str(i) + " секунд "
        if phrase.startswith(txt3):
            set_timer_real(core, i, txt)
            return

    for i in range(100, 1, -1):
        txt = num_to_text.num2text(i, female_units_min) + " "
        if phrase.startswith(txt):
            set_timer_real(core, i*60, txt)
            return

        txt2 = num_to_text.num2text(i, female_units_min2) + " "
        if phrase.startswith(txt2):
            set_timer_real(core, i*60, txt)
            return

        txt3 = str(i) + " минут "
        if phrase.startswith(txt3):
            set_timer_real(core, i*60, txt)
            return

    for i in range(100, 1, -1):
        txt = num_to_text.num2text(i, female_units_min) + " "
        txt2 = num_to_text.num2text(i) + " "
        if phrase.startswith(txt2):
            set_timer_real(core, i*60, txt)
            return

        txt3 = str(i)+" "
        if phrase.startswith(txt3):
            set_timer_real(core, i*60, txt)
            return

    if phrase.startswith("один ") or phrase.startswith("одна ") or phrase.startswith("одну "):
        txt = num_to_text.num2text(1, female_units_min)
        set_timer_real(core, 1*60, txt)
        return

    core.say("Что после таймер?")
    core.context_set(set_timer)


def set_timer_real(core: VACore, num: int, txt: str):
    core.set_timer(num,(after_timer, txt))
    core.play_voice_assistant_speech("Ставлю таймер на "+txt)


def after_timer(core: VACore, txt: str):
    options = core.plugin_options(modname)

    for i in range(options["wavRepeatTimes"]):
        core.play_wav(options["wavPath"])
        time.sleep(0.2)

    core.play_voice_assistant_speech(txt+" прошло")

if __name__ == "__main__":
    set_timer(None,"")
