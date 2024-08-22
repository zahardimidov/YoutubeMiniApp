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
    duration = ''.join(
        [i if i.isdigit() else ':' for i in video['duration'].replace('P', '')])

    msg = f'\U0001F37F <b><a href="https://www.youtube.com/watch?v={video["id"]}">{video["title"]}</a></b>\n\n\U0001F5E3: #{video["channel_title"]}\n\U0001F4C5 Дата: {video["publishedAt"]}\n\u23F1 Продолжительность: {duration}'
    await message.answer_photo(photo=data['photo'], caption=msg)
