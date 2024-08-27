import asyncio
import os
import pathlib
import threading

import redis
import yt_dlp
from dotenv import load_dotenv

video_folder = pathlib.Path(__file__).parent.parent.resolve().joinpath('video')
audio_folder = pathlib.Path(__file__).parent.parent.resolve().joinpath('audio')

if not os.path.exists(video_folder):
    os.mkdir(video_folder)

if not os.path.exists(audio_folder):
    os.mkdir(audio_folder)

load_dotenv()

HOST = os.environ.get('HOST', 'localhost')

# Connect to Redis server
r = redis.Redis(host=HOST, port=6379, db=0)


def download_video(video_id):
    ydl_opts = {
        'format': "bestvideo[ext=mp4]",
        "outtmpl": f'{video_folder}/%(id)s.%(ext)s',
    }

    filename = f'{video_folder}/{video_id}.mp4'

    if not os.path.exists(f'{audio_folder}/{video_id}.webm'):
        download_audio(video_id)

    if not os.path.exists(filename):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
            print('Complete loading')


def download_audio(video_id):
    ydl_opts = {
        'format': 'bestaudio[ext=webm]',
        'extractaudio': True,
        'outtmpl': f'{audio_folder}/%(id)s.%(ext)s',
    }

    filename = f'{audio_folder}/{video_id}.webm'

    if not os.path.exists(filename):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'https://www.youtube.com/watch?v={video_id}'])

print('DOWNLOADER STARTED')

while True:
    task: bytes = r.lpop('download_video')
    if task is not None:
        video_id = task.decode()
        target = threading.Thread(
            target=download_video, name=f'download_video_{video_id}', args=[video_id])
        target.start()

        print('Video downloading started: %s' % task)

    task: bytes = r.lpop('download_audio')
    if task is not None:
        video_id = task.decode()
        target = threading.Thread(
            target=download_video, name=f'download_audio_{video_id}', args=[video_id])
        target.start()

        print('Audio downloading started: %s' % task)


