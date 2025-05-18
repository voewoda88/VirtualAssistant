import threading
import traceback

from vacore import VACore
from websocket_creation import start_server
import time

# ------------------- main loop ------------------
if __name__ == "__main__":
    cmd_core = VACore()
    cmd_core.init_with_plugins()
    print("Command-line interface for Irina.")

    threading.Thread(target=start_server, daemon=True).start()


    # time.sleep(0.5)
    # cmd = "поставь таймер"
    # try:
    #     cmd_core.execute_next(cmd, cmd_core.context)
    # except:
    #     if cmd == "привет":
    #         print("Ошибка при запуске команды 'привет'. Скорее всего, проблема с TTS.")
    #     import traceback
    #     traceback.print_exc()

    print("Enter command (user text like 'привет') or 'exit'")
    while True:
        cmd = input("> ")
        if cmd == "exit":
            break

        cmd_core.execute_next(cmd, cmd_core.context)
