from database.schemas import WebAppRequest
from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from youtube.api import get_channel_videos, get_video, search
from pyrogram import Client
from config import BASE_DIR

api_id = '20985389'
api_hash = 'e29ea4c9df52d3f99fc0678c48a82da2'

router = APIRouter(prefix='', tags=['API сервиса'])
userbot = Client('USERBOT', api_id=api_id, api_hash=api_hash)

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


@router.post('/send_video')
async def send_video(request: Request):
    data: dict = await request.json()
    video = data.get('video')
    chat_id = data.get('chat_id')

    video_path = BASE_DIR.joinpath('video').joinpath(video)
    
    await userbot.send_video(chat_id=chat_id, video=video_path)

    return Response(status_code=200)