import json
import os
import pathlib
import threading

import redis
import yt_dlp
from dotenv import load_dotenv

video_folder = pathlib.Path(__file__).parent.parent.resolve().joinpath('video')
audio_folder = pathlib.Path(__file__).parent.parent.resolve().joinpath('audio')

load_dotenv()

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')

r = redis.Redis(host=REDIS_HOST, port=6379, db=0)


def download(video_id: str, options: dict, attempts: int = 3):
    for i in range(attempts):
        try:
            raise Exception('hi')
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
            break
        except Exception as e:
            print(f'Attempt {i+1}: {str(e)}')
    else:
        return 'error'


def download_video(data: dict):
    video_id = data['video_id']
    video_format = data['video_format']

    filepath = f'{video_folder}/{video_id}_{video_format}.mp4'

    ydl_opts = {
        'format': f'{video_format}+bestaudio',
        'outtmpl': filepath,
        'final_ext': 'mp4',
        'merge_output_format': True,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }

    if not os.path.exists(f'{video_folder}/{video_id}_{video_format}.mp4'):
        if download(video_id=video_id, options=ydl_opts) == 'error':
            return r.rpush('downloading_error', json.dumps(dict(message_id=data['message_id'], chat_id=data['chat_id'])))

    data = dict(filename=f'{video_id}_{video_format}.mp4',
                chat_id=data['chat_id'], caption=data['caption'], message_id=data['message_id'])
    r.rpush('send_file', json.dumps(data))

    print('VIDEO WAS DOWNLOADED')


def download_audio(data: dict):
    video_id = data['video_id']
    format_id = data['audio_format']

    filename = f'{audio_folder}/{video_id}.mp3'

    ydl_opts = {
        'format': format_id,
        'outtmpl': filename,
        'final_ext': 'mp3',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    if not os.path.exists(filename):
        if download(video_id=video_id, options=ydl_opts) == 'error':
            return r.rpush('downloading_error', json.dumps(dict(message_id=data['message_id'], chat_id=data['chat_id'])))

    data = dict(filename=filename, chat_id=data['chat_id'],
                caption=data['caption'], message_id=data['message_id'])
    r.rpush('send_file', json.dumps(data))

    print('AUDIO WAS DOWNLOADED')


print('DOWNLOADER STARTED')

while True:
    task: bytes = r.lpop('download')
    if task is not None:
        data = json.loads(task.decode())

        print(data)

        if data.get('video_format'):
            target = threading.Thread(
                target=download_video, args=[data])
            target.start()
        elif data.get('audio_format'):
            target = threading.Thread(
                target=download_audio, args=[data])
            target.start()

        print('Video downloading started: %s' % task)
