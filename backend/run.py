from api import router as api_router
from bot import process_update, run_bot
from bot.middlewares.webapp_user import webapp_user_middleware
from config import WEBHOOK_PATH
from database.admin import init_admin
from database.schemas import WebAppRequest
from database.session import engine, run_database
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse


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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4500, forwarded_allow_ips='*')
