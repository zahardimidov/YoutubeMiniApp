from pyrogram import Client
from telethon import TelegramClient
import asyncio

api_id = '20985389'
api_hash = 'e29ea4c9df52d3f99fc0678c48a82da2'

if __name__ == '__main__':
    async def main():
        #userbot = Client("USERBOT", api_id, api_hash)
        userbot = TelegramClient("USERBOT", api_id, api_hash)

        async with userbot:
            print(await userbot.get_me())
    asyncio.run(main())
