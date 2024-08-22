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
        'format': "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": f'{video_folder}/%(id)s.%(ext)s',
    }

    filename = f'{video_folder}/{video_id}.mp4'

    if not os.path.exists(f'{audio_folder}/{video_id}.mp3'):
        download_audio(video_id)

    if not os.path.exists(filename):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
            print('Complete loading')


def download_audio(video_id):
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'outtmpl': f'{audio_folder}/%(id)s.mp3',
    }

    filename = f'{audio_folder}/{video_id}.mp3'

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


# 139 m4a  audio only      2 │   58.59KiB   48k https │ audio only        mp4a.40.5   48k 22k low, m4a_dash
# 249 webm audio only      2 │   58.17KiB   48k https │ audio only        opus        48k 48k low, webm_dash
# 250 webm audio only      2 │   76.07KiB   63k https │ audio only        opus        63k 48k low, webm_dash
# 140 m4a  audio only      2 │  154.06KiB  128k https │ audio only        mp4a.40.2  128k 44k medium, m4a_dash
# 251 webm audio only      2 │  138.96KiB  116k https │ audio only        opus       116k 48k medium, webm_dash
# 17  3gp  176x144     12  1 │   55.79KiB   45k https │ mp4v.20.3     45k mp4a.40.2    0k 22k 144p
# 18  mp4  640x360     30  2 │ ~525.60KiB  420k https │ avc1.42001E  420k mp4a.40.2    0k 44k 360p
# 22  mp4  1280x720    30  2 │ ~  1.82MiB 1493k https │ avc1.64001F 1493k mp4a.40.2    0k 44k 720p
