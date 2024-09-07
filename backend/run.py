from datetime import datetime, timedelta

from api import router as api_router
from bot import process_update, run_bot
from config import BASE_DIR, WEBHOOK_PATH
from database.admin import init_admin
from database.requests import get_plan, get_user, set_user
from database.schemas import WebAppRequest
from database.session import engine, run_database
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from payments import create_payment


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


@app.get('/pay')
async def pay(plan: str, user: str):
    plan = await get_plan(plan_id=plan)

    url = create_payment(plan=plan, user_id=user)

    return RedirectResponse(url)


@app.post('/payment')
async def payment(request: Request):
    data = await request.json()

    if data['object']['status'] == 'succeeded':
        data = data['object']['metadata']

        user = await get_user(user_id=data['user_id'])
        plan = await get_plan(plan_id=data['plan'])

        if not user:
            return Response(status_code=400)

        await set_user(user.id, subscription_until=datetime.now()+timedelta(days=plan.days))

    return Response(status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4500, forwarded_allow_ips='*')
