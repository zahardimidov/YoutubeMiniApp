import asyncio
import pathlib

from telethon import TelegramClient

CURRENT_DIR = pathlib.Path(__file__).parent.resolve()
API_ID = '20985389'
API_HASH = 'e29ea4c9df52d3f99fc0678c48a82da2'

# +79600471358

client = TelegramClient(CURRENT_DIR.joinpath('USERBOT'), API_ID, API_HASH)


async def main():
    await client.start()
    await client.connect()
    me = await client.get_me()
    print(me)

asyncio.run(main())
