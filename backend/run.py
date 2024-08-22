from api import router as api_router
from bot import process_update, run_bot
from bot.middlewares.webapp_user import webapp_user_middleware
from config import WEBHOOK_PATH, BASE_DIR
from database.admin import init_admin
from database.schemas import WebAppRequest
from database.session import engine, run_database
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse

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

@app.get('/download_video/{video_id}', response_class=StreamingResponse)
async def download_video(video_id: str):
    return StreamingResponse(open(video_folder.joinpath(f'{video_id}.mp4'), "rb"), media_type="video/m4a", headers={"Content-Disposition": f"attachment; filename={video_id}.mp4"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4500, forwarded_allow_ips='*')
