import aiofiles
import aiohttp
import json
import os
from datetime import datetime

import redis
from aiogram import F, Router
from aiogram.types import (CallbackQuery, ContentType, FSInputFile,
                           InlineKeyboardButton, InlineKeyboardMarkup, Message)
from bot.routers.base import get_plans_kb
from config import BASE_DIR, REDIS_HOST, WEBAPP_URL
from database.requests import (add_downloading, get_quota,
                               get_todays_downloadings, get_user)
from youtube import youtube_get_video

router = Router()
r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

video_folder = BASE_DIR.joinpath('video')
audio_folder = BASE_DIR.joinpath('audio')

empty_markup = InlineKeyboardMarkup(inline_keyboard=[[]])


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

    print(video)

    msg = f'\U0001F37F <b><a href="https://www.youtube.com/watch?v={video["id"]}">{video["title"]}</a></b>\n\n\U0001F5E3 Автор: #{video["channel"]}\n\U0001F4C5 Дата: {video["publishDate"]}\n \u23F1 Продолжительность: {video["duration"]}'

    keyboard = []

    audio_size = 0

    user = await get_user(user_id=message.from_user.id)
    quota = await get_quota()
    downloadings = await get_todays_downloadings(user_id=message.from_user.id)

    try:
        await message.delete()
    except:pass

    if (user.subscription_until == None or user.subscription_until < datetime.now().date()) and len(downloadings) >= quota:
        keyboard = [[InlineKeyboardButton(
            text='Оплатить подписку', url='https://google.com')]]
        msg += '⭐️ Лимит бесплатных скачиваний исчерпан, оплатите подписку и продолжайте скачивать видео'

        markup = await get_plans_kb(user_id=user.id)
    else:
        if video['audio_format']:
            audio_size = int(video['audio_format']['filesize'])

            callback = f'o_{video["id"]},{video["audio_format"]["format_id"]},'

            text = f'🎧 Аудио / {pretty_size(audio_size)}' + (' ⚡️ мгновенно' if os.path.exists(
                audio_folder.joinpath(f'{video["id"]}.webm')) else '')

            url = WEBAPP_URL + \
                f'/download?video_id={video["id"]}&audio_format={video["audio_format"]["format_id"]}&user={user.id}'
            keyboard.append([InlineKeyboardButton(
                text=text, callback_data=callback)])

        for v in video['video_formats']:
            video_size = int(v['filesize']) + audio_size

            if video_size / 1024 / 1024 / 1024 < 2:
                callback = f'o_{video["id"]},{video["audio_format"]["format_id"]},{v["format_id"]}'
            else:
                callback = 'error'

            print(callback)

            text = f'🎥 {v["resolution"]} / ~{pretty_size(video_size)}' + (' ⚡️ мгновенно' if os.path.exists(
                video_folder.joinpath(f'{video["id"]}_{v["format_id"]}.mp4')) else '')

            url = WEBAPP_URL + \
                f'/download?video_id={video["id"]}&video_format={v["format_id"]}&audio_format={video["audio_format"]["format_id"]}&user={user.id}'
            keyboard.append([InlineKeyboardButton(
                text=text, callback_data=callback)])

        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
            
    path = video_folder.joinpath(f'{video["id"]}.webp')

    async with aiohttp.ClientSession() as session:
        async with session.get(data['photo']) as response:
            if response.status != 200:
                raise Exception('Got non-200 response!')

            async with aiofiles.open(path, 'wb') as file:
                async for data, _ in response.content.iter_chunks():
                    await file.write(data)

    await message.answer_photo(photo=FSInputFile(path=path), caption=msg, reply_markup=markup)


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
        #downloading_text = '\n\n📥⌛ Скачиваю из источника ⌛📥'

        #try:
        #    await callback_query.message.edit_caption(caption=callback_query.message.caption + downloading_text, reply_markup=empty_markup)
        #except Exception as e:
        #    print(e)

        #caption = callback_query.message.caption.replace(downloading_text, '')

        r.rpush('download', json.dumps(dict(
            video_id=video_id,
            video_format=video_format,
            audio_format=audio_format,
            message_id = callback_query.message.message_id,
            chat_id = callback_query.message.chat.id,
            caption = callback_query.message.caption
        )))

        await add_downloading(user_id=user.id)
