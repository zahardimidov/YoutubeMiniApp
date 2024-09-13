import json
from config import BASE_DIR, REDIS_HOST
from database.schemas import WebAppRequest, Video
from fastapi import APIRouter
import redis
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from pyrogram import Client
from youtube.api import get_channel_videos, get_video, search

api_id = '20985389'
api_hash = 'e29ea4c9df52d3f99fc0678c48a82da2'

router = APIRouter(prefix='', tags=['API сервиса'])
userbot = Client('USERBOT', api_id=api_id, api_hash=api_hash)
r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

async def periodic(): 
    while True:
        task: bytes = r.lpop('send_video')
        if task is not None:
            data = json.loads(task.decode())

            await userbot.send_video(chat_id=data['chat_id'], video=BASE_DIR.joinpath('video').joinpath(data['video_name']))
            

@router.post('/search')
async def search_(request: WebAppRequest):
    data: dict = await request.json()
    q = data.get('query')

    if not q:
        return JSONResponse(content=[], status_code=400)

    elements = await search(q, maxResults=50)
    data = jsonable_encoder(elements)

    return JSONResponse(content=data)


@router.post('/channel_videos')
async def channel_videos_(request: WebAppRequest):
    data: dict = await request.json()
    channel_id = data.get('channel_id')

    if not channel_id:
        return JSONResponse(content=[], status_code=400)

    videos = await get_channel_videos(channel_id=channel_id)
    data = jsonable_encoder(videos)

    return JSONResponse(content=videos)


@router.post('/get_video')
async def video_(request: WebAppRequest):
    data: dict = await request.json()
    video_id = data.get('video_id')

    if not video_id:
        return JSONResponse(content=[], status_code=400)

    video = await get_video(video_id=video_id)

    return JSONResponse(content=video)

