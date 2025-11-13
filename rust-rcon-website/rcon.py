#!/usr/bin/env python3

from websockets import connect as websockets_connect
from json import loads as json_loads, dumps as json_dumps
from os import getenv as os_getenv
from asyncio import gather as asyncio_gather, run as asyncio_run, to_thread as asyncio_to_thread
import readline

HISTORY_FILE = ".rcon_history"
try:
    readline.read_history_file(HISTORY_FILE)
except FileNotFoundError:
    pass

internal_ws_uri = f"ws://{os_getenv('RCON_HOST')}:{os_getenv('RCON_PORT')}/{os_getenv('RCON_PASSWORD')}"

async def main():
    async with websockets_connect(internal_ws_uri, ping_timeout=None) as rcon:
        async def send_input(rcon):
            while True:
                message = await asyncio_to_thread(input, '> ')
                await rcon.send(json_dumps({
                    "Identifier": -1,
                    "Message": message,
                    "Name": "WebRcon"
                }))
        
        async def listen(rcon):
            while True:
                raw = await rcon.recv()
                message = json_loads(raw).get("Message")
                print(f'\r{message}\n> ', end="", flush=True)
        
        await asyncio_gather(
            send_input(rcon),
            listen(rcon)
        )

if __name__ == "__main__":
    try:
        asyncio_run(main())
    finally:
        readline.write_history_file(HISTORY_FILE)
