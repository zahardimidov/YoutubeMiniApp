import json

from aiogram import F, Router
from aiogram.types import ContentType, Message, InlineKeyboardMarkup, InlineKeyboardButton
from youtube import youtube_get_video
from config import WEBAPP_URL

router = Router()


@router.message(F.content_type == ContentType.WEB_APP_DATA)
async def video_receive(message: Message):
    data = json.loads(message.web_app_data.data)
    video = await youtube_get_video(data['id'])

    duration = ''.join([i if i.isdigit() else ':' for i in video['duration'][2:-1]])

    msg = f'\U0001F37F <b><a href="https://www.youtube.com/watch?v={video["id"]}">{video["title"]}</a></b>\n\n\U0001F5E3 Автор: #{video["channel_title"]}\n\U0001F4C5 Дата: {video["publishedAt"]}\n \u23F1 Продолжительность: {duration}'
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Download Audio', url=WEBAPP_URL+f'/check_audio/{video["id"]}')],
        [InlineKeyboardButton(text='Download', url=WEBAPP_URL+f'/check/{video["id"]}')]
    ])
    await message.answer_photo(photo=data['photo'], caption=msg, reply_markup=markup)
