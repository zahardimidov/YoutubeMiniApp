import os

import redis
from bot.middlewares.webapp_user import webapp_user_middleware
from config import BASE_DIR, REDIS_HOST
from database.schemas import WebAppRequest
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


@router.post('/upload_video')
async def upload_video(request: Request):
    data: dict = await request.json()
    video_id = data.get('video_id')

    r.rpush('download_video', video_id)

    return Response(status_code=200)


@router.post('/check_video')
async def check_video(request: Request):
    data: dict = await request.json()
    video_id = data.get('video_id')

    if os.path.exists(video_folder.joinpath(f'{video_id}.m4a')) and os.path.exists(audio_folder.joinpath(f'{video_id}.m4a')):
        return JSONResponse(content=jsonable_encoder({'status': 'ready'}))
    return JSONResponse(content=jsonable_encoder({'status': 'not ready'}))
