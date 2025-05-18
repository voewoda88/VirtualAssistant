import json
import re
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from vacore import VACore

# функция на старте
def start(core:VACore):
    manifest = {
        "name": "Открыть браузер по настраиваемой команде",
        "version": "1.0",
        "require_online": True,

        "commands": {

        },

        "default_options": {
            "cmds": {
                "ютуб|юту|ютюб": "https://www.youtube.com/results?search_query={}",
                "яндекс": "https://yandex.ru/search/?text={}",
                "главная яндекс|главное яндекс": "https://yandex.ru/",
            }
        }

    }
    return manifest

def start_with_options(core:VACore, manifest:dict):
    # модифицируем манифест, добавляя команды на основе options, сохраненных в файле
    cmds = {}
    cmdoptions = manifest["options"]["cmds"]
    print(cmdoptions)
    for cmd in cmdoptions.keys():
        cmds[cmd] = (open_browser, cmdoptions[cmd])

    manifest["commands"] = cmds
    return manifest

def open_browser(core:VACore, phrase:str, param: str):
    core.play_voice_assistant_speech("Открываю браузер")

    import webbrowser
    url = ""
    try:
        url = param.format(phrase)
    except Exception:
        core.play_voice_assistant_speech("Ошибка при формировании ссылки")

    if url != "":
        webbrowser.get().open(url)

def search_youtube_and_list(core: VACore, phrase: str):
    # query = phrase.replace("ютуб", "").strip()
    # # if not query:
    # #     core.play_voice_assistant_speech("Что искать на ютубе?")
    # # core.play_voice_assistant_speech(f"Ищу на ютубе {query}")
    # search_url = f"https://www.youtube.com/results?search_query={query}"
    #
    # headers = {
    #     "User-Agent": "Mozilla/5.0"
    # }
    #
    # response = requests.get(search_url, headers=headers)
    #
    # if response.status_code != 200:
    #     # core.play_voice_assistant_speech("Извините, но мне не удалось получить результат.")
    #     return
    #
    # soup = BeautifulSoup(response.text, "html.parser")
    #
    # scripts = soup.find_all("script")
    # yt_data_script = None
    # for script in scripts:
    #     if script.string and "ytInitialData" in script.string:
    #         yt_data_script = script.string
    #         break
    #
    # if not yt_data_script:
    #     raise ValueError("ytInitialData not found")
    #
    # # Извлекаем JSON (ищем между 'ytInitialData = ' и концом JSON)
    # match = re.search(r"ytInitialData\s*=\s*(\{.*?\});", yt_data_script, re.DOTALL)
    # if not match:
    #     raise ValueError("Could not extract ytInitialData JSON")
    #
    # json_str = match.group(1)
    #
    # # Преобразуем в объект Python
    # yt_initial_data = json.loads(json_str)
    #
    # # videos = soup.find_all("a", {"href": True})
    # # video_links = []
    # # for v in videos:
    # #     href = v.get("href")
    # #     if href.startswith("/watch") and href not in video_links:
    # #         video_links.append(href)
    # #
    # # if not video_links:
    # #     # core.play_voice_assistant_speech("Видео не найдены")
    # #     return
    #
    # contents = yt_initial_data["contents"]["twoColumnBrowseResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"][]
    #
    # max_videos = 5
    # for i, link in enumerate(video_links[:max_videos], start=1):
    #     print(f"{i}. https://www.youtube.com{link}")

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    driver.get("https://www.youtube.com/results?search_query=кот+говорит+мяу")

    time.sleep(3)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    thumbnails = soup.find_all('ytd-thumbnail')

    for thumb in thumbnails:
        a_tag = thumb.find('a', {'id': 'thumbnail'})
        if a_tag and a_tag.has_attr('href') and '/watch?v=' in a_tag['href']:
            link = "https://www.youtube.com" + a_tag['href']
            print(link)

if __name__ == "__main__":
    search_youtube_and_list(None, "ютуб котики")


