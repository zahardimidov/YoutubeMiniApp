from threading import Thread

from bot.middlewares.webapp_user import webapp_user_middleware
from database.schemas import WebAppRequest
from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from youtube import (get_video_status,
                     youtube_get_channel_videos, youtube_get_video,
                     youtube_search)

router = APIRouter(prefix='', tags=['API сервиса'])

tasks_state = {}

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

'''
@router.post('/upload_video')
async def upload_video_(request: Request, background_tasks: BackgroundTasks):
    data: dict = await request.json()
    video_id = data.get('video_id')

    background_tasks.add_task(upload_video, video_id)

    return Response(status_code=200)

@router.get('/get_video_status/{video_id}')
async def get_video_status_(video_id: str):
    status = get_video_status(video_id=video_id)
    
    print(status)

    return Response(status_code=200)
'''