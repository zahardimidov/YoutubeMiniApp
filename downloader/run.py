import redis
import threading
import yt_dlp
import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.environ.get('HOST', 'localhost')

# Connect to Redis server
r = redis.Redis(host=HOST, port=6379, db=0)

def download(video_id):
    ydl_opts = {
        'format': "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": 'videos/%(id)s.%(ext)s',
    }

    filename = f'videos/{video_id}.mp4'

    if not os.path.exists(filename):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
            print('Complete loading')

print('DOWNLOADER STARTED')

while True:
    # Get a task from the queue
    task: bytes = r.lpop('tasks')
    
    # Process the task
    if task is not None:
        video_id = task.decode()
        target = threading.Thread(target=download, name=f'download_video_{video_id}', args=[video_id])
        target.start()

        print('Task started: %s' % task)