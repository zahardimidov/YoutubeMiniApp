import asyncio
import json
import os
import pathlib

import uvloop
from asyncio_atexit import register as atexit
from dotenv import load_dotenv
from pyrogram import Client
from redis import Redis

load_dotenv()
uvloop.install()

BASE_DIR = pathlib.Path(__file__).parent.parent.resolve()
SESSION_NAME = os.environ.get('SESSION_NAME', 'USERBOT')
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')

userbot = Client(SESSION_NAME)
redis = Redis(REDIS_HOST)

async def progress(current, total):
    print(f"{current * 100 / total:.1f}%")

async def send_file(data):
    print(data)
    await userbot.send_video('me', video=BASE_DIR.joinpath('video').joinpath('shack.mp4'), progress=progress, supports_streaming=True)


async def main():
    await userbot.start()
    atexit(userbot.stop)

    while True:
        task: bytes = redis.lpop('send_file')

        if task is not None:
            data: dict = json.loads(task.decode())
            asyncio.create_task(send_file(data))

        await asyncio.sleep(1)

asyncio.run(main())
