import asyncio
import json
import os
import random
import ssl
from functools import partial, wraps

import aiohttp
import certifi
import requests
import yt_dlp

email = 'yapi4198@gmail.com'
password = 'yapi3340@gmail.com'


# ssl.create_default_context(cafile=certifi.where())˝

API_URL = "https://www.googleapis.com/youtube/v3/"
API_KEYS = [
    'AIzaSyAG78TY-KZFgN9Qc5UYlMsdPHGBUppGkSo'
]


async def youtube_get(method, maxResults=1, **kwargs):
    CHROME = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
              'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36')

    headers = requests.utils.default_headers()
    headers['User-Agent'] = random.choice(CHROME)

    params = {
        'key': random.choice(API_KEYS),
        'part': 'id,snippet' if method == 'search' else 'statistics,snippet,contentDetails',
        'maxResults': maxResults
    }
    params.update(**kwargs)

    async with aiohttp.ClientSession(headers=headers) as session:
        response = await session.get(API_URL + method, params=params)
        data: dict = await response.json()

        return data


async def youtube_search(query, maxResults):
    data: dict = await youtube_get('search', maxResults=maxResults, q=query, type='video,channel')

    return [YoutubeObject.from_data(el) for el in data.get('items', [])]


async def youtube_get_video(video_id='9GeW5T-c1Yw'):
    data: dict = await youtube_get('videos', id=video_id)

    print(json.dumps(data, indent=4, ensure_ascii=False))

    return YoutubeObject.from_data(data['items'][0]) if data.get('items', []) else None


async def youtube_get_channel(channel_id='UCw3vK8lNe5SZzL--rMgq-CQ'):
    data: dict = await youtube_get('channels', id=channel_id)

    return YoutubeObject.from_data(data['items'][0]) if data.get('items', []) else None


async def youtube_get_channel_videos(channel_id='UCw3vK8lNe5SZzL--rMgq-CQ', count=50):
    data = await youtube_get('search', maxResults=count, channelId=channel_id, order='date', type='video')

    return [YoutubeObject.from_data(el) for el in data.get('items', [])]


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
            'photo': data['snippet']['thumbnails']['high']['url'],
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


uploading = {}
video_folder = 'video'


def get_video_status(video_id):
    filename = f'{video_folder}/{video_id}.mp4'

    if os.path.exists(filename):
        return 'uploaded',
    if video_id in uploading:
        return 'uploading', uploading.get(video_id)
    return None,


def hook(*args, **kwargs):
    process_video_id = args[0]['info_dict']['id']
    uploading[process_video_id] = args[0]['_percent_str']


def wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run


'''
def upload_video_(video_id):
    filename = f'{video_folder}/{video_id}.mp4'

    ydl_opts = {
        'format': "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": 'videos/%(id)s.%(ext)s',
        "progress_hooks": [hook],
        'proxy': 'http://nMee0T:wfqXV3@186.179.61.101:9743'
    }

    if not os.path.exists(filename):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'https://www.youtube.com/watch?v={video_id}'])

def upload_video(video_id):

    filename = f'{video_folder}/{video_id}.mp4'

    ydl_opts = {
        'format': "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": 'videos/%(id)s.%(ext)s',
        "progress_hooks": [hook],
        'proxy': 'http://nMee0T:wfqXV3@186.179.61.101:9743'
    }

    if not os.path.exists(filename):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'https://www.youtube.com/watch?v={video_id}'])'''

'''
    cmd = f'yt-dlp -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best -outtmpl '
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    await upload_video_(video_id)'''

if __name__ == '__main__':
    asyncio.run(youtube_get_video())
