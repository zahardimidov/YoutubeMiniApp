import os
import pathlib
import threading
import json
import redis
import yt_dlp
from dotenv import load_dotenv
import subprocess
import time
import requests

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


def download_video(data):
    video_id = data['video_id']
    video_format = data['video_format']

    ydl_opts = {
        'format': video_format,
        "outtmpl": f'{video_folder}/%(id)s_%(format_id)s_temp.%(ext)s',
    }

    if not os.path.exists(f'{audio_folder}/{video_id}.webm'):
        download_audio(data)

    if not os.path.exists(f'{video_folder}/{video_id}_{video_format}.mp4'):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'https://www.youtube.com/watch?v={video_id}'])

        time.sleep(3)

        command = [
            'ffmpeg',
            '-i', video_folder.joinpath(f'{video_id}_{video_format}_temp.mp4'),
            '-i', audio_folder.joinpath(f'{video_id}.webm'),
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

        requests.post('https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/sendVideo', data=dict(chat_id = data['chat_id'], video = f'{video_folder}/{video_id}_{video_format}.mp4'))

        


def download_audio(data):
    video_id = data['video_id']
    format_id = data['audio_format']

    ydl_opts = {
        'format': format_id,
        'outtmpl': f'{audio_folder}/%(id)s.%(ext)s',
    }

    if not os.path.exists(f'{audio_folder}/{video_id}.webm'):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'https://www.youtube.com/watch?v={video_id}'])


print('DOWNLOADER STARTED')

while True:
    task: bytes = r.lpop('download')
    if task is not None:
        data = json.loads(task.decode())

        if data.get('video_format'):
            target = threading.Thread(
                target=download_video, args=[data])
            target.start()
        elif data.get('audio_format'):
            target = threading.Thread(
                target=download_audio, args=[data])
            target.start()

        print('Video downloading started: %s' % task)