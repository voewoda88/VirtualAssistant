import os
import traceback
import hashlib

from termcolor import colored, cprint
import time
from threading import Timer

from typing import Dict

from jaa import JaaCore

from collections.abc import Callable

version = "10.9.4"


class VACore(JaaCore):
    def __init__(self):
        JaaCore.__init__(self)

        self.timers = [-1, -1, -1, -1, -1, -1, -1, -1]
        self.timersFuncUpd = [None, None, None, None, None, None, None, None]
        self.timersFuncEnd = [None, None, None, None, None, None, None, None]
        self.timersDuration = [0, 0, 0, 0, 0, 0, 0, 0]

        self.commands = {
        }

        self.plugin_commands = {
        }

        self.ttss = {
        }

        self.playwavs = {
        }

        self.fuzzy_processors: Dict[str, tuple[Callable,Callable]] = {
        }

        # more options
        self.mpcHcPath = ""
        self.mpcIsUse = False
        self.mpcIsUseHttpRemote = False

        self.isOnline = False
        self.version = version

        self.voiceAssNames = []
        self.voiceAssNameRunCmd = {}

        self.useTTSCache = False
        self.tts_cache_dir = "tts_cache"
        self.ttsEngineId = ""
        self.ttsEngineId2 = ""
        self.playWavEngineId = ""

        self.logPolicy = ""
        self.tmpdir = "temp"
        self.tmpcnt = 0

        self.lastSay = ""
        self.remoteTTS = "none"
        self.remoteTTSResult = None

        self.context = None
        self.contextTimer = None
        self.contextTimerLastDuration = 0

        self.contextDefaultDuration = 10
        self.contextRemoteWaitForCall = False

        import mpcapi.core
        self.mpchc = mpcapi.core.MpcAPI()

        self.cur_callname:str = ""

        self.input_cmd_full:str = ""

        self.fastApiApp = None

    def init_with_plugins(self):
        self.init_plugins(["core"])
        self.display_init_info()

        self.setup_assistant_voice()

    # ----------- process plugins functions ------
    def process_plugin_manifest(self, modname, manifest):
        plugin_req_online = True
        if "require_online" in manifest:
            plugin_req_online = manifest["require_online"]

        if "commands" in manifest:
            for cmd in manifest["commands"].keys():
                if not self.isOnline and plugin_req_online:
                    self.commands[cmd] = self.stub_online_required
                else:
                    self.commands[cmd] = manifest["commands"][cmd]

                if modname in self.plugin_commands:
                    self.plugin_commands[modname].append(cmd)
                else:
                    self.plugin_commands[modname] = [cmd]

        if "tts" in manifest:
            for cmd in manifest["tts"].keys():
                self.ttss[cmd] = manifest["tts"][cmd]

        if "playwav" in manifest:
            for cmd in manifest["playwav"].keys():
                self.playwavs[cmd] = manifest["playwav"][cmd]

        if "fuzzy_processor" in manifest:
            for cmd in manifest["fuzzy_processor"].keys():
                self.fuzzy_processors[cmd] = manifest["fuzzy_processor"][cmd]

    def stub_online_required(self, core, phrase):
        self.play_voice_assistant_speech(self.plugin_options("core")["replyOnlineRequired"])

    def print_error(self, err_txt, e: Exception = None):
        cprint(err_txt, "red")
        import traceback
        traceback.print_exc()

    def print_red(self,txt):
        cprint(txt, "red")

    # ----------- text-to-speech functions ------

    def setup_assistant_voice(self):
        try:
            self.playwavs[self.playWavEngineId][0](self)
        except Exception as e:
            self.print_error("Ошибка инициализации плагина проигрывания WAV (playWavEngineId)", e)
            self.print_red('Попробуйте установить в options/core.json: "playWavEngineId": "sounddevice"')
            self.print_red('...временно переключаюсь на консольный вывод ответа...')
            self.ttsEngineId = "console"

        try:
            self.ttss[self.ttsEngineId][0](self)
        except Exception as e:
            self.print_error("Ошибка инициализации плагина TTS (ttsEngineId)", e)
            cprint('Попробуйте установить в options/core.json: "ttsEngineId": "console" для тестирования вывода через консоль', "red")
            cprint('Позднее, если все заработает, вы сможете настроить свой TTS-движок', "red")

            from sys import platform
            if platform == "linux" or platform == "linux2":
                cprint("Подробнее об установке на Linux: https://github.com/janvarev/Irene-Voice-Assistant/blob/master/docs/INSTALL_LINUX.md", "red")
            elif platform == "darwin":
                cprint("Подробнее об установке на Mac: https://github.com/janvarev/Irene-Voice-Assistant/blob/master/docs/INSTALL_MAC.md", "red")
            elif platform == "win32":
                #cprint("Подробнее об установке на Linux: https://github.com/janvarev/Irene-Voice-Assistant/blob/master/docs/INSTALL_LINUX.md", "red")
                pass

            self.print_red('...временно переключаюсь на консольный вывод ответа...')
            self.ttsEngineId = "console"

        if self.ttsEngineId2 == "":
            self.ttsEngineId2 = self.ttsEngineId
        if self.ttsEngineId2 != self.ttsEngineId:
            try:
                self.ttss[self.ttsEngineId2][0](self)
            except Exception as e:
                self.print_error("Ошибка инициализации плагина TTS2 (ttsEngineId2)", e)

        for k in self.fuzzy_processors.keys():
            try:
                self.fuzzy_processors[k][0](self)
            except Exception as e:
                self.print_error("Ошибка инициализации fuzzy_processor {0}".format(k), e)

    def play_voice_assistant_speech(self, text_to_speech: str):
        self.lastSay = text_to_speech
        remoteTTSList = self.remoteTTS.split(",")

        self.remoteTTSResult = {}
        is_processed = False

        if "none" in remoteTTSList:
            if self.ttss[self.ttsEngineId][1] != None:
                self.ttss[self.ttsEngineId][1](self,text_to_speech)
            else:
                if self.useTTSCache:
                    tts_file = self.get_tts_cache_file(text_to_speech)
                else:
                    tts_file = self.get_tempfilename()+".wav"

                if not self.useTTSCache or self.useTTSCache and not os.path.exists(tts_file):
                    self.tts_to_filewav(text_to_speech, tts_file)

                self.play_wav(tts_file)
                if not self.useTTSCache and os.path.exists(tts_file):
                    os.unlink(tts_file)

            is_processed = True

        if "saytxt" in remoteTTSList:
            self.remoteTTSResult["restxt"] = text_to_speech

            is_processed = True

        if "saywav" in remoteTTSList:
            if self.useTTSCache:
                tts_file = self.get_tts_cache_file(text_to_speech)
            else:
                tts_file = self.get_tempfilename()+".wav"

            if not self.useTTSCache or self.useTTSCache and not os.path.exists(tts_file):
                self.tts_to_filewav(text_to_speech, tts_file)

            import base64

            with open(tts_file, "rb") as wav_file:
                encoded_string = base64.b64encode(wav_file.read())

            if not self.useTTSCache and os.path.exists(tts_file):
                os.unlink(tts_file)

            self.remoteTTSResult["wav_base64"] = encoded_string

            is_processed = True

        if not is_processed:
            print("Ошибка при выводе TTS - remoteTTS не был обработан.")
            print("Текущий remoteTTS: {}".format(self.remoteTTS))
            print("Текущий remoteTTSList: {}".format(remoteTTSList))
            print("Ожидаемый remoteTTS (например): 'none'")

    def say(self, text_to_speech: str):
        self.play_voice_assistant_speech(text_to_speech)

    def say2(self, text_to_speech: str):
        if self.ttss[self.ttsEngineId2][1] != None:
            self.ttss[self.ttsEngineId2][1](self,text_to_speech)
        else:
            tempfilename = self.get_tempfilename()+".wav"
            self.tts_to_filewav2(text_to_speech, tempfilename)
            self.play_wav(tempfilename)
            if os.path.exists(tempfilename):
                os.unlink(tempfilename)

    def tts_to_filewav(self, text_to_speech: str, filename: str):
        if len(self.ttss[self.ttsEngineId]) > 2:
            self.ttss[self.ttsEngineId][2](self, text_to_speech, filename)
        else:
            print("File save not supported by this TTS")

    def tts_to_filewav2(self, text_to_speech: str, filename: str):
        if len(self.ttss[self.ttsEngineId2]) > 2:
            self.ttss[self.ttsEngineId2][2](self, text_to_speech, filename)
        else:
            print("File save not supported by this TTS")

    def get_tempfilename(self):
        self.tmpcnt += 1
        return self.tmpdir+"/vacore_"+str(self.tmpcnt)

    def get_tts_cache_file(self, text_to_speech: str):
        hash = hashlib.md5(text_to_speech.encode('utf-8')).hexdigest()
        text_slice = text_to_speech[:40]
        filename = ".".join([text_slice, hash, "wav"])
        return self.tts_cache_dir+"/"+self.ttsEngineId+"/"+filename

    def all_num_to_text(self, text: str):
        from utils.all_num_to_text import all_num_to_text
        return all_num_to_text(text)

    # -------- main function ----------
    def find_best_cmd_with_fuzzy(self, command, context, allow_rest_phrase = True, threshold: float = None):
        """
        Поиск оптимальной команды с учетом обработчиков нечеткого сравнения

        - command - команда
        - context - в формате Ирининого контекста (словарь {"cmd":"val",...}) - с элементами контекста будет сравниваться в поиске команды
        - allow_rest_phrase - дана ли в команде вся команда, или она может быть продолжена в контексте? не все нечеткие сравнители обрабатывают корректно
        Пример:
        allow_rest_phrase=True: привет как дела -> привет (отлично подходит, будет вернута rest_phrase как дела)
        allow_rest_phrase=False: привет как дела -> привет (подходит не очень, будет вернута rest_phrase "")
        - threshold - в случае нечеткого сравнения - порог схожести (от 0.0 до 1.0). Если лучший результат сравнения ниже порога, результат не будет возвращен.
        Если None / не указано - будет браться из параметров core ядра Ирины.

        Возвращает tuple(key_in_context, схожесть (от 0.0 до 1.0), res_phrase)
        """

        # первый проход - ищем полное совпадение
        for keyall in context.keys():
            keys = keyall.split("|")
            for key in keys:
                if command == key:
                    return (keyall, 1.0, "")

        if allow_rest_phrase: # если фраза может быть неполной
            # второй проход - ищем частичное совпадение
            for keyall in context.keys():
                keys = keyall.split("|")
                for key in keys:
                    if command.startswith(key):
                        rest_phrase = command[(len(key) + 1):]
                        return (keyall, 1.0, rest_phrase)

        if threshold is None:
            threshold = self.plugin_options("core")["fuzzyThreshold"]

        # третий проход - ищем с помощью fuzzy_processors
        # TODO: по хорошему надо пробежаться по всем процессорам, и выдать лучший результат,
        # но пока берется просто первый прошедший пороговое значение
        for fuzzy_processor_k in self.fuzzy_processors.keys():
            res = None
            try:
                res = self.fuzzy_processors[fuzzy_processor_k][1](self, command, context, allow_rest_phrase)
            except TypeError as e:
                res = self.fuzzy_processors[fuzzy_processor_k][1](self, command, context)

            # fuzzy processor должен вернуть либо None либо
            # (context_key:str,уверенность:float[0:1],rest_phrase:str) для лучшей фразы
            print("Fuzzy processor {0}, result for '{1}': {2}".format(fuzzy_processor_k, command, res))

            if res is not None:
                keyall, probability, rest_phrase = res
                if threshold < probability:
                    return res

        return None

    def execute_next(self, command, context):
        if context == None:
            context = self.commands
            self.input_cmd_full = command

        if isinstance(context,dict):
            pass
        else:
            self.context_clear()
            self.call_ext_func_phrase(command, context)
            return

        try:
            res = self.find_best_cmd_with_fuzzy(command, context, True)
            if res is not None:
                keyall, probability, rest_phrase = res
                next_context = context[keyall]
                self.execute_next(rest_phrase, next_context)
                return

            if self.context == None:
                self.say(self.plugin_options("core")["replyNoCommandFound"])
            else:
                self.say(self.plugin_options("core")["replyNoCommandFoundInContext"])
                if self.contextTimer != None:
                    self.context_set(self.context, self.contextTimerLastDuration)
        except Exception as err:
            print(traceback.format_exc())

    def fuzzy_get_command_key_from_context(self, predicted_command: str, context: dict):
        # возвращает ключ в context по одной из распознанных команд внутри
        # нужно для fuzzy, так как одним из возвратов должен быть КЛЮЧ в контексте, а не команда
        for keyall in context.keys():
            for key in keyall.split("|"):
                if key == predicted_command:
                    return keyall
        return None

    # ----------- timers -----------
    def util_time_to_readable(self, curtime):
        import datetime
        human_readable_date_local = datetime.datetime.fromtimestamp(curtime)

        return human_readable_date_local.strftime('%Y-%m-%d %H:%M:%S')

    def set_timer(self, duration, timerFuncEnd, timerFuncUpd = None):
        curtime = time.time()
        for i in range(len(self.timers)):
            if self.timers[i] <= 0:
                self.timers[i] = curtime+duration
                self.timersFuncEnd[i] = timerFuncEnd
                print("New Timer ID =", str(i), ' curtime=', self.util_time_to_readable(curtime), 'duration=', duration, 'endtime=', self.util_time_to_readable(self.timers[i]))
                return i
        return -1

    def clear_timer(self, index, runEndFunc=False):
        if runEndFunc and self.timersFuncEnd[index] != None:
            self.call_ext_func(self.timersFuncEnd[index])
        self.timers[index] = -1
        self.timersDuration[index] = 0
        self.timersFuncEnd[index] = None

    def clear_timers(self):
        for i in range(len(self.timers)):
            if self.timers[i] >= 0:
                self.timers[i] = -1
                self.timersFuncEnd[i] = None

    def _update_timers(self):
        curtime = time.time()
        for i in range(len(self.timers)):
            if(self.timers[i] > 0):
                if curtime >= self.timers[i]:
                    print("End Timer ID =", str(i), ' curtime=', self.util_time_to_readable(curtime), 'endtime=', self.util_time_to_readable(self.timers[i]))
                    self.clear_timer(i,True)

    # --------- calling functions -----------

    def call_ext_func(self, funcparam):
        if isinstance(funcparam, tuple):
            funcparam[0](self, funcparam[1])
        else:
            funcparam(self)

    def call_ext_func_phrase(self, phrase, funcparam):
        if isinstance(funcparam, tuple):
            funcparam[0](self, phrase, funcparam[1])
        else:
            funcparam(self, phrase)

    # ------- play wav from subfolder ----------
    def play_wav(self, wavfile):
        self.playwavs[self.playWavEngineId][1](self, wavfile)


    # -------- raw txt running -----------------
    def run_input_str(self, voice_input_str, func_before_run_cmd = None): # voice_input_str - строка распознавания голоса, разделенная пробелами
                # пример: "ирина таймер пять"
        haveRun = False
        if voice_input_str == None:
            return False

        if self.logPolicy == "all":
            if self.context == None:
                print("Input: ", voice_input_str)
            else:
                print("Input (in context): ", voice_input_str)

        try:
            voice_input = voice_input_str.split(" ")
            haveRun = False
            if self.context == None:
                for ind in range(len(voice_input)):
                    callname = voice_input[ind]

                    if callname in self.voiceAssNames:
                        self.cur_callname = callname
                        if self.logPolicy == "cmd":
                            print("Input (cmd): ", voice_input_str)

                        command_options = " ".join([str(input_part) for input_part in voice_input[(ind+1):len(voice_input)]])
                        if callname in self.voiceAssNameRunCmd:
                            command_options = self.voiceAssNameRunCmd.get(callname)+" "+command_options
                            print("Modified input, added ", self.voiceAssNameRunCmd.get(callname))

                        if func_before_run_cmd != None:
                            func_before_run_cmd()

                        self.execute_next(command_options, None)
                        haveRun = True
                        break
            else:
                if self.logPolicy == "cmd":
                    print("Input (cmd in context): ", voice_input_str)

                if func_before_run_cmd != None:
                    func_before_run_cmd()

                self.execute_next(voice_input_str, self.context)
                haveRun = True

        except Exception as err:
            print(traceback.format_exc())

        return haveRun

    # ------------ context handling functions ----------------

    def context_set(self, context, duration=None):
        if duration == None:
            duration = self.contextDefaultDuration

        self.context_clear()

        self.context = context
        self.contextTimerLastDuration = duration
        self.contextTimer = Timer(duration,self._context_clear_timer)

        remoteTTSList = self.remoteTTS.split(",")
        if self.contextRemoteWaitForCall and ("saytxt" in remoteTTSList or "saywav" in remoteTTSList):
            pass
        else:
            self.contextTimer.start()

    def _context_clear_timer(self):
        print("Context cleared after timeout")
        self.contextTimer = None
        self.context_clear()

    def context_clear(self):
        self.context = None
        if self.contextTimer != None:
            self.contextTimer.cancel()
            self.contextTimer = None

    # ----------- display info functions ------

    def display_init_info(self):
        cprint("VoiceAssistantCore v{0}:".format(version), "blue", end=' ')
        print("run ONLINE" if self.isOnline else "run OFFLINE")

        self.format_print_key_list("TTS engines", self.ttss.keys())
        self.format_print_key_list("PlayWavs engines", self.playwavs.keys())
        self.format_print_key_list("FuzzyProcessor engines", self.fuzzy_processors.keys())
        self.format_print_key_list("Assistant names", self.voiceAssNames)

        cprint("Commands list: "+"#"*65, "blue")
        for plugin in self.plugin_commands:
            self.format_print_key_list(plugin, self.plugin_commands[plugin])
        cprint("#"*80, "blue")

    def format_print_key_list(self, key: str, value: list):
        print(colored(key+": ", "blue")+", ".join(value))
