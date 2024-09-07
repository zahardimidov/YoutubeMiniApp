from database.schemas import WebAppRequest
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from youtube.api import get_channel_videos, get_video, search

router = APIRouter(prefix='', tags=['API сервиса'])

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
