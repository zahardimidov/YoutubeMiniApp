import json
from datetime import datetime

import redis
from aiogram import F, Router
from aiogram.types import (CallbackQuery, ContentType, FSInputFile,
                           InlineKeyboardButton, InlineKeyboardMarkup, Message)
from bot.routers.base import get_plans_kb
from config import REDIS_HOST
from database.requests import get_quota, get_todays_downloadings, get_user
from pyrogram import Client
from youtube.api import (check_audio, check_video, download_audio,
                         download_video, get_video)

router = Router()
empty_markup = InlineKeyboardMarkup(inline_keyboard=[[]])
r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

def pretty_size(b: int):
    b = b / 1024

    if b > 512:
        return f'{round(b / 1024, 2)} MB'
    else:
        return f'{round(b, 2)} KB'
    


@router.message(F.content_type == ContentType.WEB_APP_DATA)
async def video_receive(message: Message):
    data = json.loads(message.web_app_data.data)
    video = await get_video(data['id'])

    msg = f'\U0001F37F <b><a href="https://www.youtube.com/watch?v={video["id"]}">{video["title"]}</a></b>\n\n\U0001F5E3 Автор: #{video["channel"]}\n\U0001F4C5 Дата: {video["publishDate"]}\n \u23F1 Продолжительность: {video["duration"]}'

    keyboard = []

    audio_size = 0

    user = await get_user(user_id=message.from_user.id)
    quota = await get_quota()
    downloadings = await get_todays_downloadings(user_id = message.from_user.id)

    if (user.subscription_until == None or user.subscription_until < datetime.now().date()) and len(downloadings) >= quota:
        msg += '⭐️ Лимит бесплатных скачиваний исчерпан, оплатите подписку и продолжайте скачивать видео'
        markup = await get_plans_kb(user_id=user.id)
    else:
        if video['audio_format']:
            audio_size = int(video['audio_format']['filesize'])
            callback = f'o_{video["id"]},{video["audio_format"]["format_id"]},' if audio_size / 1024 / 1024 / 1024 < 2 else 'error'

            text = f'🎧 Аудио / {pretty_size(audio_size)}'
            if check_audio(video_id=video['id']):
                text += ' ⚡️ мгновенно'

            keyboard.append([InlineKeyboardButton(text=text, callback_data=callback)])

        for v in video['video_formats']:
            video_size = int(v['filesize']) + audio_size
            callback = f'o_{video["id"]},{video["audio_format"]["format_id"]},{v["format_id"]}' if video_size / 1024 / 1024 / 1024 < 2 else 'error'

            text = f'🎥 {v["resolution"]} / ~{pretty_size(video_size)}'
            if check_video(video_id=video['id'], video_format=v['format_id']):
                text += ' ⚡️ мгновенно'

            keyboard.append([InlineKeyboardButton(text=text, callback_data=callback)])

        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    try: await message.delete()
    except:pass
    await message.answer_photo(photo=video['photo'], caption=msg, reply_markup=markup)


@router.callback_query(F.data == "error")
async def answer(callback: CallbackQuery):
    await callback.answer('😕 Telegram не позволяет отправлять файлы таких размеров, выберите другой формат')


@router.callback_query(F.data.startswith('o_'))
async def callback_download(callback_query: CallbackQuery):
    video_id, audio_format, video_format = callback_query.data[2:].split(',')

    user = await get_user(user_id=callback_query.from_user.id)
    quota = await get_quota()
    downloadings = await get_todays_downloadings(user_id=user.id)

    if (user.subscription_until == None or user.subscription_until < datetime.now().date()) and len(downloadings) >= quota:
        plans = await get_plans_kb(callback_query.from_user.id)
        await callback_query.message.edit_reply_markup(reply_markup=empty_markup)
        return await callback_query.message.answer('⭐️ Лимит бесплатных скачиваний исчерпан, оплатите подписку', reply_markup=plans)

    else:
        downloading_text = '\n\n📥⌛ Скачиваю из источника ⌛📥'
        caption = callback_query.message.caption

        data = dict(
            chat_id = callback_query.message.chat.id,
            message_id = callback_query.message.message_id,
            video_id=video_id,
            video_format=video_format,
            audio_format=audio_format
        )

        print(data)

        r.rpush('download', json.dumps(data))