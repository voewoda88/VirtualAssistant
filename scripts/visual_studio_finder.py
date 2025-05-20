import json
import os
import threading
from queue import Queue
from string import ascii_uppercase


def search_drive(drive, target_filename, result_queue):
    for root, dirs, files in os.walk(drive, topdown=True):
        if target_filename in files:
            full_path = os.path.join(root, target_filename)
            result_queue.put(full_path)
            return


def find_vscode_path_and_update_json(json_path):
    try:
        if not os.path.exists(json_path):
            print(f"Конфигурационный файл не найден: {json_path}")
            return None

        with open(json_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        existing_path = config.get("Path")

        if existing_path and os.path.isfile(existing_path):
            print(f"Путь к VS Code уже настроен: {existing_path}")
            return existing_path

        print("Идёт поиск Visual Studio Code...")

        target_filename = "Code.exe"
        result_queue = Queue()
        drives = [f"{d}:\\\\" for d in ascii_uppercase if os.path.exists(f"{d}:\\")]

        threads = []
        for drive in drives:
            t = threading.Thread(target=search_drive, args=(drive, target_filename, result_queue))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        if not result_queue.empty():
            found_path = result_queue.get()
            print(f"Найден VS Code: {found_path}")

            config["Path"] = found_path
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return found_path
        else:
            print("VS Code не найден.")
            return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None


def start_vscode_path_resolution(json_config_path):
    thread = threading.Thread(target=find_vscode_path_and_update_json, args=(json_config_path,), daemon=True)
    thread.start()
    return thread
