import os
import pathlib
import threading
import json
import redis
import yt_dlp
from dotenv import load_dotenv
import subprocess
import time

api_id = '20985389'
api_hash = 'e29ea4c9df52d3f99fc0678c48a82da2'


if __name__ == '__main__':
    import asyncio
    import uvloop

    from pyrogram import Client


    async def main():
        client = Client("USERBOT", api_id, api_hash)

        async with client:
            print(await client.get_me())

userbot = Client("USERBOT", api_id, api_hash)

video_folder = pathlib.Path(__file__).parent.parent.resolve().joinpath('video')
audio_folder = pathlib.Path(__file__).parent.parent.resolve().joinpath('audio')

load_dotenv()

HOST = os.environ.get('HOST', 'localhost')

r = redis.Redis(host=HOST, port=6379, db=0)

downloading_text = '\n\n📥⌛ Скачиваю из источника ⌛📥'

def download_video(data: dict):
    video_id = data['video_id']
    video_format = data['video_format']

    ydl_opts = {
        'format': video_format,
        "outtmpl": f'{video_folder}/%(id)s_%(format_id)s_temp.%(ext)s',
    }

    chat_id = data.pop('chat_id')
    message_id = data.pop('message_id')

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

        loop = asyncio.new_event_loop()
        loop.run_until_complete(userbot.send_video(chat_id=chat_id, video=f'{video_folder}/{video_id}_{video_format}.mp4'))



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

    if data.get('chat_id') and data.get('message_id'):
        #title = ''.join([i for i in data['caption'] if i.isalpha()][:20])
        loop = asyncio.new_event_loop()
        loop.run_until_complete(userbot.send_audio(chat_id=data['chat_id'], video=f'{audio_folder}/{video_id}.webm'))



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


