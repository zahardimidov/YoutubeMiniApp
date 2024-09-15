from sqlalchemy import select

from database.models import User, Quota, Plan, Downloading, File
from database.session import async_session
from datetime import datetime, timedelta


async def get_user(user_id) -> User:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == int(user_id)))

        return user
    

async def get_plan(plan_id) -> Plan:
    async with async_session() as session:
        plan = await session.scalar(select(Plan).where(Plan.id == plan_id))

        return plan
    
    
async def get_quota() -> int:
    async with async_session() as session:
        quota = await session.scalar(select(Quota))

        return quota.quota
    

async def get_plans() -> list[Plan]:
    async with async_session() as session:
        plans = await session.scalars(select(Plan))

        return plans.all()


async def set_user(user_id, **kwargs) -> User:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == user_id))

        if not user:
            user = User(id=user_id, **kwargs)
            session.add(user)
        else:
            for k, v in kwargs.items():
                setattr(user, k, v)

        await session.commit()
        await session.refresh(user)

        return user

async def add_downloading(user_id):
    async with async_session() as session:
        downloading = Downloading(user_id=user_id, date = datetime.now())
        session.add(downloading)
        
        await session.commit()

async def get_todays_downloadings(user_id):
    async with async_session() as session:
        downloadings = await session.scalars(select(Downloading).where(Downloading.user_id == user_id, Downloading.date > datetime.now() - timedelta(days=1)))

        return downloadings.all()
    

async def get_plans():
    async with async_session() as session:
        plans = await session.scalars(select(Plan).order_by(Plan.price))

        return plans.all()
async def get_file(filename):
    async with async_session() as session:
        file = await session.scalar(select(File).where(File.filename == filename))

        if file:
            return await file.exists()

        return file