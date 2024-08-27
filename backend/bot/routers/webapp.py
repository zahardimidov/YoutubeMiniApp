import json

from aiogram import F, Router
from aiogram.types import (ContentType, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from config import WEBAPP_URL
from youtube import youtube_get_video

router = Router()


@router.message(F.content_type == ContentType.WEB_APP_DATA)
async def video_receive(message: Message):
    data = json.loads(message.web_app_data.data)
    video = await youtube_get_video(data['id'])

    msg = f'\U0001F37F <b><a href="https://www.youtube.com/watch?v={video["id"]}">{video["title"]}</a></b>\n\n\U0001F5E3 Автор: #{video["channel"]}\n\U0001F4C5 Дата: {video["publishDate"]}\n \u23F1 Продолжительность: {video["duration"]}'

    keyboard = []

    audio_size = 0
    if video['audio_format']:
        audio_size = video['audio_format']['filesize']
        url = WEBAPP_URL + f'/download?video_id={video["id"]}&audio_format={video["audio_format"]["format_id"]}'
        keyboard.append([InlineKeyboardButton(text=f'audio / {audio_size} MB', url=url)])

    for v in video['video_formats']:
        video_size = v['filesize'] / 1048576
        url = WEBAPP_URL + f'/download?video_id={video["id"]}&video_format={v["format_id"]}&audio_format{video["audio_format"]["format_id"]}'
        keyboard.append([InlineKeyboardButton(text=f'{v["resolution"]} / ~{video_size} MB', url=url)])

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer_photo(photo=data['photo'], caption=msg, reply_markup=markup)
