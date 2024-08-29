import asyncio
from io import BytesIO

from api import router as api_router
from bot import process_update, run_bot
from bot.middlewares.webapp_user import webapp_user_middleware
from config import BASE_DIR, WEBHOOK_PATH
from database.admin import init_admin
from database.schemas import WebAppRequest, User
from database.session import engine, run_database
from database.requests import get_user, get_quota, set_user, get_todays_downloadings, add_downloading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse, Response
from datetime import datetime
from fastapi.encoders import jsonable_encoder


video_folder = BASE_DIR.joinpath('video')
audio_folder = BASE_DIR.joinpath('audio')


async def on_startup(app: FastAPI):
    init_admin(app=app, engine=engine)
    await run_database()
    await run_bot()

    yield

app = FastAPI(lifespan=on_startup)
app.add_api_route(WEBHOOK_PATH, endpoint=process_update, methods=['post'])
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        '*'
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/', response_class=HTMLResponse)
async def home(request: WebAppRequest):
    return f'<div style="display: flex; width: 100vw; height: 100vh; justify-content: center; background-color: #F9F9F9; color: #03527E;"> <b style="margin-top:35vh">Welcome!</b> </div>'


@app.get('/download', response_class=StreamingResponse)
async def download(user: int, video_id: str, audio_format: str = None, video_format: str = None):
    user: User = await get_user(user_id=user)
    quota = await get_quota()
    downloadings = await get_todays_downloadings(user_id = user.id)

    if (user.subscription_until == None or user.subscription_until < datetime.now().date()) and len(downloadings) >= quota:
        return Response(status_code=403)
    else:
        await add_downloading(user_id=user.id)


    if audio_format and not video_format:
        return StreamingResponse(open(audio_folder.joinpath(f'{video_id}.webm'), "rb"), media_type="audio/webm", headers={"Content-Disposition": f"attachment; filename={video_id}.webm"})
    command = [
        'ffmpeg',
        '-i', video_folder.joinpath(f'{video_id}_{video_format}.mp4'),
        '-i', audio_folder.joinpath(f'{video_id}.webm'),
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-f', 'mp4',
        '-movflags', 'frag_keyframe+empty_moov',
        'pipe:1'
    ]

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    imgio = BytesIO(stdout)

    return StreamingResponse(imgio, media_type="video/mp4", headers={"Content-Disposition": f"attachment; filename={video_id}.mp4"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4500, forwarded_allow_ips='*')
