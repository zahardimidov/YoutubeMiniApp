import asyncio
import json
import random

import requests
from aiohttp import ClientSession

email = 'yapi4198@gmail.com'
password = 'yapi3340@gmail.com'

API_URL = "https://www.googleapis.com/youtube/v3/"

API_KEYS = [
    'AIzaSyAG78TY-KZFgN9Qc5UYlMsdPHGBUppGkSo'
]

CHROME = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
          'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36')


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
        if fmt['audio_ext'] != 'none' and fmt['video_ext'] == 'none' and fmt.get('filesize'):
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
    try:
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
    except:
        return 'error'


async def get_channel(channel_id):
    data: dict = await _make_request('channels', id=channel_id)
    results = data.get('items', [])

    return YoutubeObject.from_data(results[0]) if results else None


async def get_channel_videos(channel_id, count=50):
    data = await _make_request('search', maxResults=count, channelId=channel_id, order='date', type='video')
    results = data.get('items', [])

    return [YoutubeObject.from_data(el) for el in results]


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
