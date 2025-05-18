import os

from vacore import VACore
from thefuzz import fuzz

modname = os.path.basename(__file__)[:-3]


def start(core: VACore):
    manifest = {
        "name": "Fuzzy text by TheFuzz lib",
        "version": "1.1",
        "require_online": False,

        "fuzzy_processor": {
            "thefuzz": (init, predict)
        }
    }
    return manifest


def init(core: VACore):
    pass


def predict(core: VACore, command: str, context: dict, allow_rest_phrase: bool = True):
    bestres = 0
    bestret = None

    for keyall in context.keys():
        keys = keyall.split("|")
        for key in keys:
            if allow_rest_phrase:
                cmdsub = command[0:len(key)]
                rest_phrase = command[(len(key)+1):]
            else:
                cmdsub = command
                rest_phrase = ""

            res = fuzz.WRatio(cmdsub, key)
            if res > bestres:
                bestres = res
                bestret = (keyall, float(res)/100, rest_phrase)

    return bestret
