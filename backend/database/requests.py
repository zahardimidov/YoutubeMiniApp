from sqlalchemy import select

from database.models import User
from database.session import async_session


async def get_user(user_id) -> User:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == user_id))

        return user


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
