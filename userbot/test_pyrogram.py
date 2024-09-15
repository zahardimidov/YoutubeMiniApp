import asyncio

import uvloop
from pyrogram import Client

SESSION_NAME = 'USERBOT'
API_ID = '20985389'
API_HASH = 'e29ea4c9df52d3f99fc0678c48a82da2'

# +79600471358

async def main():
    userbot = Client(SESSION_NAME, API_ID, API_HASH)

    await userbot.start()
    me = await userbot.get_me()
    print(me)
    await userbot.stop()


uvloop.install()
asyncio.run(main())
