import json

from aiogram import F, Router
from aiogram.types import ContentType, Message
from config import WEBAPP_URL

router = Router()


@router.message(F.content_type == ContentType.WEB_APP_DATA)
async def video_receive(message: Message):
    data = json.loads(message.web_app_data.data)
    msg = f'\U0001F37F {data["title"]}\n\U0001F4CE https://www.youtube.com/watch?v={data["id"]}\n\n\uFE0FАвтор: #{data["channel_title"]}\n\U0001F4C5 Дата: {data["publishedAt"]}\n\uFE0F Продолжительность: {data["duration"]}'
    print(data)
    await message.answer_photo(photo=data['photo'], caption=msg)
