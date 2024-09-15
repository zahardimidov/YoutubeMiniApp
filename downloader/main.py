import json
import os
import pathlib
import subprocess
import threading
import time

import redis
import yt_dlp
from dotenv import load_dotenv

video_folder = pathlib.Path(__file__).parent.parent.resolve().joinpath('video')
audio_folder = pathlib.Path(__file__).parent.parent.resolve().joinpath('audio')

load_dotenv()

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')

r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

def download_video(data: dict):
    video_id = data['video_id']
    video_format = data['video_format']

    ydl_opts = {
        'format': video_format,
        "outtmpl": f'{video_folder}/%(id)s_%(format_id)s_temp.%(ext)s',
    }

    chat_id = data.pop('chat_id')

    if not os.path.exists(f'{video_folder}/{video_id}_{video_format}.mp4'):
        if not os.path.exists(f'{audio_folder}/{video_id}.webm'):
            download_audio(data)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'https://www.youtube.com/watch?v={video_id}'])

        time.sleep(3)

        command = [
            'ffmpeg',
            '-i', video_folder.joinpath(f'{video_id}_{video_format}_temp.mp4'),
            '-i', audio_folder.joinpath(f'{video_id}.webm'),
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-strict', 'experimental',
            '-f', 'mp4',
            '-movflags', 'faststart',
            f'{video_folder}/{video_id}_{video_format}.mp4'
        ]

        subprocess.run(command)

        time.sleep(3)

        os.remove(f'{video_folder}/{video_id}_{video_format}_temp.mp4')

        print('Complete video loading')

    data = dict(filename = f'{video_id}_{video_format}.mp4', chat_id = chat_id, caption = data['caption'], message_id = data['message_id'])
    r.rpush('send_file', json.dumps(data))

    print('COMPLETE VIDEO')


def download_audio(data: dict):
    video_id = data['video_id']
    format_id = data['audio_format']

    ydl_opts = {
        'format': format_id,
        'outtmpl': f'{audio_folder}/%(id)s.%(ext)s',
    }

    if not os.path.exists(f'{audio_folder}/{video_id}.webm'):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'https://www.youtube.com/watch?v={video_id}'])

    if data.get('chat_id'):
        data = dict(filename = f'{audio_folder}/{video_id}.webm', chat_id = data['chat_id'], caption = data['caption'], message_id = data['message_id'])
        r.rpush('send_file', json.dumps(data))

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
