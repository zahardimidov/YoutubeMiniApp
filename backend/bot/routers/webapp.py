import json

from aiogram import F, Router
from aiogram.types import (ContentType, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from config import WEBAPP_URL
from youtube import youtube_get_video
from database.requests import get_user, get_quota, get_todays_downloadings
from datetime import datetime
from bot.routers.base import get_plans_kb

router = Router()

def pretty_size(b: int):
    b = b / 1024

    if b > 512:
        return f'{round(b / 1024, 2)} MB'
    else:
        return f'{round(b, 2)} KB'
    


@router.message(F.content_type == ContentType.WEB_APP_DATA)
async def video_receive(message: Message):
    data = json.loads(message.web_app_data.data)
    video = await youtube_get_video(data['id'])

    msg = f'\U0001F37F <b><a href="https://www.youtube.com/watch?v={video["id"]}">{video["title"]}</a></b>\n\n\U0001F5E3 Автор: #{video["channel"]}\n\U0001F4C5 Дата: {video["publishDate"]}\n \u23F1 Продолжительность: {video["duration"]}'

    keyboard = []

    audio_size = 0

    user = await get_user(user_id=message.from_user.id)
    quota = await get_quota()
    downloadings = await get_todays_downloadings(user_id = message.from_user.id)

    if (user.subscription_until == None or user.subscription_until < datetime.now().date()) and len(downloadings) >= quota:
        keyboard = [[InlineKeyboardButton(text='Оплатить подписку', url='https://google.com')]]
        msg += '\n\n\U0000203C превышен лимит скачиваний за день, оплати подписку, чтобы продолжить прямо сейчас'

        markup = await get_plans_kb(user_id=user.id)
    else:
        if video['audio_format']:
            audio_size = int(video['audio_format']['filesize'])

            url = WEBAPP_URL + f'/download?video_id={video["id"]}&audio_format={video["audio_format"]["format_id"]}&user={user.id}'
            keyboard.append([InlineKeyboardButton(text=f'🎧 Аудио / {pretty_size(audio_size)}', url=url)])

        for v in video['video_formats']:
            video_size = int(v['filesize']) + audio_size
            url = WEBAPP_URL + f'/download?video_id={video["id"]}&video_format={v["format_id"]}&audio_format={video["audio_format"]["format_id"]}&user={user.id}'
            keyboard.append([InlineKeyboardButton(text=f'🎥 {v["resolution"]} / ~{pretty_size(video_size)}', url=url)])

        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer_photo(photo=data['photo'], caption=msg, reply_markup=markup)
