from fastapi import FastAPI
import uvicorn

from starlette.responses import HTMLResponse
from termcolor import cprint
import json
from starlette.websockets import WebSocket
from fastapi_utils_tasks import repeat_every
from jaa import load_options
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from vacore import VACore
import time
import os

webapi_options = None

core = None
model = None

if not os.path.exists('runva_webapi.json'):
    if os.path.exists('options/webapi.json'):
        os.rename('options/webapi.json','runva_webapi.json')

default_options = {
    "host": "127.0.0.1",
    "port": 5003,
    "log_level": "info",
    "use_ssl": False
}

webapi_options = load_options(py_file=__file__,default_options=default_options)
use_ssl = webapi_options["use_ssl"]

"""
returnFormat Варианты:
- "none" (TTS реакции будут на сервере) (звук на сервере)
- "saytxt" (сервер вернет текст, TTS будет на клиенте) (звук на клиенте)
- "saywav" (TTS на сервере, сервер отрендерит WAV и вернет клиенту, клиент его проиграет) (звук на клиенте) **наиболее универсальный для клиента**
"""


def runCmd(cmd: str,returnFormat: str):
    if core.logPolicy == "cmd" or core.logPolicy == "all":
        print("Running cmd: ",cmd)

    tmpformat = core.remoteTTS
    core.remoteTTS = returnFormat
    core.remoteTTSResult = ""
    core.lastSay = ""
    core.execute_next(cmd,core.context)
    core.remoteTTS = tmpformat

app = FastAPI()
is_running = True

app.mount("/webapi_client", StaticFiles(directory="webapi_client", html = True), name="webapi_client")

app.mount("/mic_client", StaticFiles(directory="mic_client", html = True), name="mic_client")


@app.websocket("/wsrawtext")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("New WebSocket text connection")
    while True:
        data = await websocket.receive_text()

        data_json = None
        try:
            data_json = json.loads(str(data))
        except:
            print("Can't parse json from websocket: ", data)

        if data_json is not None:
            r = sendRawTxtOrig(data_json.get("txt",""), data_json.get("returnFormat", "none"))
            await websocket.send_text(str(r))


@app.websocket("/wsrawtextcmd")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("New WebSocket text cmd connection")
    while True:
        data = await websocket.receive_text()
        data_json = None
        try:
            data_json = json.loads(str(data))
        except:
            print("Can't parse json from websocket: ", data)

        if data_json is not None:
            r = sendSimpleTxtCmd(data_json.get("txt",""), data_json.get("returnFormat", "none"))
            await websocket.send_text(str(r))


@app.websocket("/wsmic")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    if model != None:
        from vosk import KaldiRecognizer
        rec = KaldiRecognizer(model, 48000)
        print("New WebSocket microphone recognition")
        while True:
            data = await websocket.receive_bytes()
            r = process_chunk(rec,data,"saytxt,saywav")
            await websocket.send_text(r)
    else:
        print("Can't accept WebSocket microphone recognition - no Model (seems to be no VOSK at startup)")


@app.websocket("/wsmic_48000_none")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    if model != None:
        from vosk import KaldiRecognizer
        rec = KaldiRecognizer(model, 48000)
        print("New WebSocket microphone recognition wsmic_48000_none")
        while True:
            data = await websocket.receive_bytes()
            r = process_chunk(rec,data,"none")
            await websocket.send_text(r)
    else:
        print("Can't accept WebSocket microphone recognition - no Model (seems to be no VOSK at startup)")


@app.websocket("/wsmic_22050_none")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    if model != None:
        from vosk import KaldiRecognizer
        rec = KaldiRecognizer(model, 22050)
        print("New WebSocket microphone recognition wsmic_22050_none")
        while True:
            data = await websocket.receive_bytes()
            r = process_chunk(rec,data,"none")
            await websocket.send_text(r)
    else:
        print("Can't accept WebSocket microphone recognition - no Model (seems to be no VOSK at startup)")


@app.websocket("/wsmic_44100_none")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    if model != None:
        from vosk import KaldiRecognizer
        rec = KaldiRecognizer(model, 44100)
        print("New WebSocket microphone recognition wsmic_44100_none")
        while True:
            data = await websocket.receive_bytes()
            r = process_chunk(rec,data,"none")
            await websocket.send_text(r)
    else:
        print("Can't accept WebSocket microphone recognition - no Model (seems to be no VOSK at startup)")


def process_chunk(rec, message, returnFormat):
    if message == '{"eof" : 1}':
        return rec.FinalResult()
    elif rec.AcceptWaveform(message):
        res2 = "{}"
        res = rec.Result()
        resj = json.loads(res)
        if "text" in resj:
            voice_input_str = resj["text"]
            import requests

            if voice_input_str != "" and voice_input_str != None:
                print(voice_input_str)
                res2 = sendRawTxtOrig(voice_input_str, returnFormat)

                if res2 != "NO_VA_NAME":
                    res3: dict = res2
                    if res3.get("wav_base64") is not None:
                        res3["wav_base64"] = res2["wav_base64"].decode("utf-8")
                    res2 = json.dumps(res3)
                else:
                    res2 = "{}"

        else:
            pass

        return res2
    else:
        res = rec.PartialResult()
        return rec.PartialResult()


@app.get("/", response_class=HTMLResponse)
async def main_page():
    from vacore import version
    html_content = f"""
    <html>
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>Irene Voice Assistant</title>
            <link rel="stylesheet" href="/webapi_client/chota.min.css">
        </head>
        <body>
            <div id="top" class="container" role="document">
                <h1>Irene Voice Assistant {version}</h1>

                <a href="/webapi_client" class="button">Web interface (simple, STT in browser)</a><br /><br />
                
                <a href="/mic_client" class="button">Web interface (simple, only microphone listen)</a><br /><br />

                <a href="/docs" class="button">API and docs</a><br /><br />

                <a href="https://github.com/janvarev/Irene-Voice-Assistant" class="button" target="_blank">Github</a><br /><br />
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.on_event("startup")
async def startup_event():
    global core
    core = VACore()
    core.fastApiApp = app
    core.init_with_plugins()

    from vacore import version

    print(f"WEB api for VoiceAssistantCore {version} (remote control)")

    url = ""
    if webapi_options["use_ssl"]:
        url = "https://{0}:{1}/".format("localhost",webapi_options["port"])
    else:
        url = "http://{0}:{1}/".format("localhost",webapi_options["port"])

    print("Web client URL (main page): ", url )
    print("Web client URL (VOSK in browser): ", url+"webapi_client/")
    print("Mic client URL (experimental, sends WAV bytes to server): ", url+"mic_client/")

    try:
        import vosk
        from vosk import Model, SpkModel, KaldiRecognizer
        global model
        model = Model("model")
    except Exception as e:
        print("Can't init VOSK - no websocket speech recognition in WEBAPI. Can be skipped")
        import traceback
        traceback.print_exc()


@app.get("/ttsWav")
async def ttsWav(text:str):
    #runCmd(cmd,returnFormat)
    tmpformat = core.remoteTTS
    core.remoteTTS = "saywav"
    core.play_voice_assistant_speech(text)
    core.remoteTTS = tmpformat
    return core.remoteTTSResult


@app.get("/sendTxtCmd")
async def sendSimpleTxtCmd(cmd:str,returnFormat:str = "none"):
    runCmd(cmd,returnFormat)
    return core.remoteTTSResult


@app.get("/sendRawTxt")
async def sendRawTxt(rawtxt:str,returnFormat:str = "none"):
    return sendRawTxtOrig(rawtxt,returnFormat)


def sendRawTxtOrig(rawtxt:str,returnFormat:str = "none"):
    tmpformat = core.remoteTTS
    core.remoteTTS = returnFormat
    core.remoteTTSResult = ""
    core.lastSay = ""
    isFound = core.run_input_str(rawtxt)
    core.remoteTTS = tmpformat

    if isFound:
        return core.remoteTTSResult
    else:
        return "NO_VA_NAME"


@app.get("/reinitContext")
async def reinitContext():
    if core.contextTimer != None:
        core.context_set(core.context,core.contextTimerLastDuration)
    return ""


@app.get("/updTimers")
async def updTimers():
    #core.say("аа")
    #print("upd timers")
    core._update_timers()
    return ""


@app.get("/replyWasGiven")
async def replyWasGiven():
    if core.contextRemoteWaitForCall:
        if core.contextTimer != None:
            core.contextTimer.start()


def core_update_timers_http(runReq=True):
    while is_running:
        try:
            import requests
            if webapi_options["use_ssl"]:
                reqstr = "https://{0}:{1}/updTimers".format(webapi_options["host"],webapi_options["port"])
            else:
                reqstr = "http://{0}:{1}/updTimers".format(webapi_options["host"],webapi_options["port"])
            r = requests.get(reqstr, verify=False)
        except Exception:
            pass

        try:
            time.sleep(2)
        except:
            return

    return


@app.on_event("shutdown")
def app_shutdown():
    global is_running
    cprint("Ctrl-C pressed, exiting Irene.", "yellow")
    is_running = False


@app.on_event("startup")
@repeat_every(seconds=2)
async def app_timers():
    if core != None:
        core._update_timers()


if __name__ == "__main__":
    if webapi_options["use_ssl"]:
        uvicorn.run("runva_webapi:app",
                    host=webapi_options["host"], port=webapi_options["port"],
                    ssl_keyfile="localhost.key",
                    ssl_certfile="localhost.crt",
                    log_level=webapi_options["log_level"])
    else:
        uvicorn.run("runva_webapi:app",
                    host=webapi_options["host"], port=webapi_options["port"],
                    log_level=webapi_options["log_level"])