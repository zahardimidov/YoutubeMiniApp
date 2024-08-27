import asyncio
import os
import pathlib
import threading
import json
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


def download_video(video):
    video_id = video['video_id']
    format_id = video['format_id']

    ydl_opts = {
        'format': format_id,
        "outtmpl": f'{video_folder}/%(id)s_%(format_id)s.%(ext)s',
    }

    if not os.path.exists(f'{audio_folder}/{video_id}.webm'):
        download_audio(video_id)

    if not os.path.exists(f'{video_folder}/{video_id}_{format_id}.mp4'):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
            print('Complete loading')


def download_audio(video):
    print(video, type(video))
    video_id = video['video_id']
    format_id = video['format_id']

    ydl_opts = {
        'format': format_id,
        'extractaudio': True,
        'outtmpl': f'{audio_folder}/%(id)s.%(ext)s',
    }

    if not os.path.exists(f'{audio_folder}/{video_id}.webm'):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'https://www.youtube.com/watch?v={video_id}'])


print('DOWNLOADER STARTED')

while True:
    task: bytes = r.lpop('download_video')
    if task is not None:
        video = json.loads(task.decode())
        target = threading.Thread(
            target=download_video, args=[video])
        target.start()

        print('Video downloading started: %s' % task)

    task: bytes = r.lpop('download_audio')
    if task is not None:
        video = json.loads(task.decode())
        target = threading.Thread(
            target=download_video, args=[video])
        target.start()

        print('Audio downloading started: %s' % task)
