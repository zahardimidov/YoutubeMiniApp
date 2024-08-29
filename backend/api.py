import json
import os

import redis
from bot.middlewares.webapp_user import webapp_user_middleware
from config import BASE_DIR, REDIS_HOST
from database.schemas import WebAppRequest, User
from database.requests import get_user, get_quota, get_todays_downloadings
from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from youtube import (youtube_get_channel_videos, youtube_get_video,
                     youtube_search)

router = APIRouter(prefix='', tags=['API сервиса'])
r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

video_folder = BASE_DIR.joinpath('video')
audio_folder = BASE_DIR.joinpath('audio')

# @router.post('/search')
# @webapp_user_middleware


@router.post('/search')
async def search(request: WebAppRequest):
    data: dict = await request.json()
    q = data.get('query')

    if not q:
        return JSONResponse(content=[], status_code=400)

    elements = await youtube_search(q, maxResults=50)
    data = jsonable_encoder(elements)

    return JSONResponse(content=data)


# @router.post('/channel_videos')
# @webapp_user_middleware

@router.post('/channel_videos')
async def channel_videos(request: WebAppRequest):
    data: dict = await request.json()
    channel_id = data.get('channel_id')

    if not channel_id:
        return JSONResponse(content=[], status_code=400)

    videos = await youtube_get_channel_videos(channel_id=channel_id)
    data = jsonable_encoder(videos)

    return JSONResponse(content=videos)


@router.post('/get_video')
async def channel_videos(request: WebAppRequest):
    data: dict = await request.json()
    video_id = data.get('video_id')

    if not video_id:
        return JSONResponse(content=[], status_code=400)

    video = await youtube_get_video(video_id=video_id)

    return JSONResponse(content=video)


@router.post('/upload')
async def upload(request: Request):
    data: dict = await request.json()

    r.rpush('download', json.dumps(data))

    return Response(status_code=200)


@router.post('/download')
async def download(request: Request):
    data: dict = await request.json()
    video_id = data.get('video_id')
    video_format = data.get('video_format')
    audio_format = data.get('audio_format')

    user: User = await get_user(user_id=data.get('user'))
    quota = await get_quota()
    downloadings = await get_todays_downloadings(user_id = user.id)

    if (user.subscription_until == None or user.subscription_until < datetime.now().date()) and len(downloadings) >= quota:
        return JSONResponse(content=jsonable_encoder({'status': 'subscribe'}))

    if video_format:
        if os.path.exists(video_folder.joinpath(f'{video_id}_{video_format}.mp4')) and os.path.exists(audio_folder.joinpath(f'{video_id}.webm')):
            return JSONResponse(content=jsonable_encoder({'status': 'ready'}))
    elif audio_format:
        if os.path.exists(audio_folder.joinpath(f'{video_id}.webm')):
            return JSONResponse(content=jsonable_encoder({'status': 'ready'}))
    return JSONResponse(content=jsonable_encoder({'status': 'not ready'}))
