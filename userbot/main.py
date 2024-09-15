import asyncio
import json
import os
import pathlib

from dotenv import load_dotenv
from redis import Redis
from telethon import TelegramClient

load_dotenv()

BASE_DIR = pathlib.Path(__file__).parent.parent.resolve()
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
API_ID = '20985389'
API_HASH = 'e29ea4c9df52d3f99fc0678c48a82da2'

client = TelegramClient('USERBOT', API_ID, API_HASH)
redis = Redis(REDIS_HOST)


async def progress(current, total):
    print(f"{current * 100 / total:.1f}%")


async def send_file(receiver, data):
    print(receiver, data)
    filename = data['filename']

    if '.mp4' in filename:
        filepath = BASE_DIR.joinpath('video').joinpath(filename)
    else:
        filepath = BASE_DIR.joinpath('audio').joinpath(filename)

    user = data['user_id']
    caption = data['caption'] + f'\n\n\n({user=})'
    await client.send_file(receiver, caption=caption, file=filepath, progress_callback=progress)


async def main():
    await client.start()
    await client.connect()
    username = await client.get_entity('Download_Tubebot')

    while True:
        task: bytes = redis.lpop('send_file')

        if task is not None:
            data: dict = json.loads(task.decode())
            asyncio.create_task(send_file(receiver=username, data=data))

        await asyncio.sleep(1)

asyncio.run(main())
