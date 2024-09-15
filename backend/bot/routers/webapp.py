import json
from datetime import datetime

import redis
from aiogram import F, Router
from aiogram.types import (CallbackQuery, ContentType, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from bot.routers.base import get_plans_kb
from config import REDIS_HOST
from database.requests import (get_file, get_quota, get_todays_downloadings,
                               get_user, add_downloading, set_file)
from youtube.api import get_video

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
    downloadings = await get_todays_downloadings(user_id=message.from_user.id)

    if (user.subscription_until == None or user.subscription_until < datetime.now().date()) and len(downloadings) >= quota:
        msg += '\n\n<b>⭐️ Лимит бесплатных скачиваний исчерпан, оплатите подписку и продолжайте скачивать видео</b>'
        markup = await get_plans_kb(user_id=user.id)
    else:
        if video['audio_format']:
            print(video["audio_format"]["format_id"])
            audio_size = int(video['audio_format']['filesize'])
            callback = f'o_{video["id"]},{video["audio_format"]["format_id"]},' if audio_size / \
                1024 / 1024 / 1024 < 2 else 'error'

            file = await get_file(f'{video["id"]}_{video["audio_format"]["format_id"]}.webm')
            if file:
                keyboard.append([InlineKeyboardButton(
                    text=f'🎧 Аудио / {pretty_size(audio_size)}', callback_data=callback)])
            else:
                keyboard.append([InlineKeyboardButton(
                    text=f'🎧 Аудио / {pretty_size(audio_size)}', callback_data=callback)])

        for v in video['video_formats']:
            video_size = int(v['filesize']) + audio_size
            callback = f'o_{video["id"]},{video["audio_format"]["format_id"]},{v["format_id"]}' if video_size / \
                1024 / 1024 / 1024 < 2 else 'error'

            file = await get_file(f'{video["id"]}_{v["format_id"]}.mp4')
            if file:
                keyboard.append([InlineKeyboardButton(
                    text=f'🎥 {v["resolution"]} / ~{pretty_size(video_size)} ⚡️ мгновенно', callback_data=callback)])
            else:
                keyboard.append([InlineKeyboardButton(
                    text=f'🎥 {v["resolution"]} / ~{pretty_size(video_size)}', callback_data=callback)])

        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    try:
        await message.delete()
    except:
        pass
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
        try:
            await callback_query.message.edit_caption(caption=callback_query.message.caption+'\n\n📥⌛ <b>Скачиваю из источника</b> ⌛📥', reply_markup=empty_markup)
        except Exception as e:print(e)

        data = dict(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            video_id=video_id,
            video_format=video_format,
            audio_format=audio_format,
            caption=callback_query.message.caption
        )

        if video_format:
            file = await get_file(f'{video_id}_{video_format}.mp4')
            if file:
                return await callback_query.message.answer_video(video=file.file_id, caption=callback_query.message.caption)

        elif audio_format:
            file = await get_file(f'{video_id}_{audio_format}.webm')
            if file:
                return await callback_query.message.answer_audio(audio=file.file_id, caption=callback_query.message.caption)

        r.rpush('download', json.dumps(data))


@router.message(F.video, F.from_user.id == 6865748575)
async def video(message: Message):
    caption, data = message.caption.split('(data(')
    caption = caption.strip()

    user_id, message_id = data.split(')(')
    user_id = int(''.join([d for d in user_id if d.isdigit()]))
    message_id = int(''.join([d for d in message_id if d.isdigit()]))

    await set_file(filename=message.video.file_name, file_id=message.video.file_id)
    await add_downloading(user_id=user_id)
    await message.bot.send_video(chat_id=user_id, caption=caption, video=message.video.file_id)
    try:
        await message.bot.delete_message(chat_id=user_id, message_id=message_id)
    except:pass


@router.message(F.content_type == ContentType.DOCUMENT, F.from_user.id == 6865748575)
async def audio(message: Message):
    caption, data = message.caption.split('(data(')
    caption = caption.strip()

    user_id, message_id = data.split(')(')
    user_id = int(''.join([d for d in user_id if d.isdigit()]))
    message_id = int(''.join([d for d in message_id if d.isdigit()]))

    title = ''.join([i for i in caption if i.isdigit()])[:15]

    await set_file(filename=message.document.file_name, file_id=message.document.file_id)
    await add_downloading(user_id=user_id)
    await message.bot.send_audio(chat_id=user_id, caption=caption, audio=message.document.file_id, title=title)
    try:
        await message.bot.delete_message(chat_id=user_id, message_id=message_id)
    except:pass

    