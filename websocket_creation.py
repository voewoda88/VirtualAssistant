import asyncio
import json
import threading
import websockets


connected = set()


async def handler(websocket):
    connected.add(websocket)
    print("Расширение подключено.")
    try:
        async for _ in websocket:
            pass
    finally:
        connected.remove(websocket)
        print("Расширение отключено.")


async def send_command(command, query):
    message = json.dumps({"command": command, "query": query})
    if connected:
        await asyncio.wait([asyncio.create_task(ws.send(message)) for ws in connected])
    else:
        print("Нет подключенных расширений")


async def main():
    async with websockets.serve(handler, "localhost", 9999):
        print("WebSocket сервер запущен на ws://localhost:9999")
        await asyncio.Future()


def start_server():
    asyncio.run(main())