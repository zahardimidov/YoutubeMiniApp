import json

from aiogram import F, Router
from aiogram.types import ContentType, Message
from config import WEBAPP_URL
from youtube import youtube_get_video

router = Router()


@router.message(F.content_type == ContentType.WEB_APP_DATA)
async def video_receive(message: Message):
    data = json.loads(message.web_app_data.data)
    video = await youtube_get_video(data['id'])
    msg = f'\U0001F37F {data["title"]}\n\U0001F4CE https://www.youtube.com/watch?v={video["id"]}\n\n\uFE0FАвтор: #{video["channel_title"]}\n\U0001F4C5 Дата: {video["publishedAt"]}\n\uFE0F Продолжительность: {video["duration"]}'
    print(video)
    await message.answer_photo(photo=data['photo'], caption=msg)
