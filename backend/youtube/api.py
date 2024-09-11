import asyncio
import json
import os
import random
import subprocess
import time
from aiogram.types import (ContentType, InlineKeyboardButton, FSInputFile,
                           InlineKeyboardMarkup, Message)

from pyrogram import Client

import requests
from aiohttp import ClientSession
from config import BASE_DIR
from .const import *
from yt_dlp import YoutubeDL

video_folder = BASE_DIR.joinpath('video')
audio_folder = BASE_DIR.joinpath('audio')
headers = requests.utils.default_headers()

async def _make_request(method, maxResults=1, **kwargs):
    headers['User-Agent'] = random.choice(CHROME)

    params = {
        'key': random.choice(API_KEYS),
        'part': 'id,snippet' if method == 'search' else 'statistics,snippet,contentDetails',
        'maxResults': maxResults
    }
    params.update(**kwargs)

    async with ClientSession(headers=headers) as session:
        response = await session.get(API_URL + method, params=params)
        data: dict = await response.json()

        return data
    
def _get_formats(info_dict: dict) -> tuple[dict, list[dict]]:
    formats = info_dict.get('formats', [])

    video_formats = []
    video_resolutions = []
    audio_format = None
    for fmt in formats:
        if fmt['audio_ext'] != 'none' and fmt['video_ext'] == 'none' and fmt.get('filesize') and fmt['ext'] == 'webm':
            if audio_format == None or audio_format['filesize'] < fmt['filesize']:
                audio_format = dict(filesize=fmt['filesize'], format_id=fmt['format_id'], ext=fmt['ext'],
                                    format_note=fmt['format_note'], resolution=fmt['resolution'], url=fmt['url'])
        if fmt['video_ext'] != 'none' and fmt['audio_ext'] == 'none' and fmt.get('filesize') and not fmt['format_note'] in video_resolutions:
            video_formats.append(
                dict(filesize=fmt['filesize'], format_id=fmt['format_id'], ext=fmt['ext'],
                     format_note=fmt['format_note'], resolution=fmt['resolution'], url=fmt['url'])
            )
            video_resolutions.append(fmt['format_note'])

    video_formats.sort(key=lambda x: x['filesize'])

    return audio_format, video_formats
    

async def search(query, maxResults):
    data: dict = await _make_request('search', maxResults=maxResults, q=query, type='video,channel')
    results = data.get('items', [])

    return [YoutubeObject.from_data(el) for el in results]


async def get_video(video_id):
    command = [
        'yt-dlp',
        '-j',
        '--flat-playlist',
        f'https://www.youtube.com/watch?v={video_id}'
    ]

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    # Parse the JSON output
    info_dict: dict = json.loads(stdout)

    title = info_dict['title']
    channel = info_dict['channel']
    photo = info_dict['thumbnail']

    print(photo)

    audio_format, video_formats = _get_formats(info_dict=info_dict)

    publishDate = info_dict['upload_date'][-2:]+"." + \
        info_dict['upload_date'][4:6]+'.'+info_dict['upload_date'][:4]

    return dict(id=video_id, title=title, publishDate=publishDate, channel=channel, duration=info_dict['duration_string'], photo=photo, audio_format=audio_format, video_formats=video_formats)


async def get_channel(channel_id):
    data: dict = await _make_request('channels', id=channel_id)
    results = data.get('items', [])

    return YoutubeObject.from_data(results[0]) if results else None


async def get_channel_videos(channel_id, count = 50):
    data = await _make_request('search', maxResults=count, channelId=channel_id, order='date', type='video')
    results = data.get('items', [])

    return [YoutubeObject.from_data(el) for el in results]

def check_audio(video_id):
    path = f'{audio_folder}/{video_id}.webm'

    if os.path.exists(path):
        return path

def check_video(video_id, video_format):
    path = f'{video_folder}/{video_id}_{video_format}.mp4'

    if os.path.exists(path):
        return path

def _download_video(data: dict):
    video_id = data['video_id']
    video_format = data['video_format']

    ydl_opts = {
        'format': video_format,
        "outtmpl": f'{video_folder}/%(id)s_%(format_id)s_temp.%(ext)s',
    }

    audio_path = f'{audio_folder}/{video_id}.webm'

    if not check_audio(video_id=video_id):
        _download_audio(data)

    if not check_video(video_id=video_id, video_format=video_format):
        try:
            print('DOWNLOAD VIDEO')
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
        except Exception as e:
            print('VIDEO DOWNLOADING ERROR:', str(e))
            return Exception('Ошибка при скачивании видео, попробуйте еще раз')

        time.sleep(3)

        command = [
            'ffmpeg',
            '-i', f'{video_folder}/{video_id}_{video_format}_temp.mp4',
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            '-f', 'mp4',
            '-movflags', 'frag_keyframe+empty_moov',
            f'{video_folder}/{video_id}_{video_format}.mp4'
        ]

        subprocess.run(command)

        time.sleep(3)
        
        os.remove(f'{video_folder}/{video_id}_{video_format}_temp.mp4')

        print('Complete loading')
        
    return f'{video_folder}/{video_id}_{video_format}.mp4'


def _download_audio(data):
    video_id = data['video_id']
    format_id = data['audio_format']

    ydl_opts = {
        'format': format_id,
        'outtmpl': f'{audio_folder}/%(id)s.%(ext)s',
    }

    path = f'{audio_folder}/{video_id}.webm'

    if not os.path.exists(path):
        try:
            print('DOWNLOAD AUDIO')
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
        except Exception as e:
            print('AUDIO DOWNLOADING ERROR:', str(e))
            return Exception('Ошибка при скачивании файла, попробуйте еще раз')

    return path


async def download_audio(data: dict):
    res = await asyncio.to_thread(_download_audio, data)
    return res

async def download_video(message: Message, data: dict):
    video_path = await asyncio.to_thread(_download_video, data)

    print(f'{video_path=}')

    api_id = '20985389'
    api_hash = 'e29ea4c9df52d3f99fc0678c48a82da2'

    async with Client("TEST", api_id, api_hash) as client:
        me = await client.get_me()
        print(me)
        await client.send_video(chat_id=message.from_user.id, video=video_path, caption=message.caption)

    await message.delete()

    


class YoutubeObject:
    @classmethod
    def from_data(cls, data: dict):
        if not data['kind'] in ['youtube#searchResult', 'youtube#video', 'youtube#channel']:
            raise Exception(f'Type of element {data["kind"]} is not available')

        if data['kind'] == 'youtube#searchResult' and type(data['id']) == dict:
            kind = data['id']['kind']
            id = data['id'].get('channelId') or data['id'].get('videoId')
        else:
            kind = data['kind']
            id = data['id']

        details = {
            'id': id,
            'title': data['snippet']['title'],
            'description': data['snippet']['description'],
            'photo': data['snippet']['thumbnails']['default']['url'],
            'type': 'channel'  # by default, but can be changed to 'video'
        }

        if 'video' in kind:
            details.update(channel_id=data['snippet']['channelId'],
                           channel_title=data['snippet']['channelTitle'], type='video')
            try:
                details.update(
                    publishedAt=data['snippet']['publishedAt'], duration=data['contentDetails']['duration'])
            except:
                pass
            return details
        elif 'channel' in kind:
            try:
                details.update(
                    subscriberCount=data['statistics']['subscriberCount'])
            except:
                pass
            return details
        

