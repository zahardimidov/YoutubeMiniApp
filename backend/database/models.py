import uuid
import aiofiles.os
import aiofiles.ospath
from config import BASE_DIR
from sqlalchemy import BigInteger, Date, DateTime, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, mapped_column


def generate_uuid():
    return str(uuid.uuid4())


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id = mapped_column(BigInteger, nullable=False, primary_key=True)
    username = mapped_column(String(50), nullable=False, primary_key=True)
    subscription_until = mapped_column(Date, nullable=True, default=None)


class Downloading(Base):
    __tablename__ = 'downloadings'

    user_id = mapped_column(BigInteger, nullable=False, primary_key=True)
    date = mapped_column(DateTime, nullable=False, primary_key=True)


class Plan(Base):
    __tablename__ = 'plans'

    id = mapped_column(String, primary_key=True, default=generate_uuid)
    days = mapped_column(Integer, nullable=False)
    price = mapped_column(Integer, nullable=False)


class Api(Base):
    __tablename__ = 'api'

    id = mapped_column(String, primary_key=True, default=generate_uuid)
    key = mapped_column(String, nullable=False)


class Quota(Base):
    __tablename__ = 'quota'

    id = mapped_column(String, primary_key=True, default=generate_uuid)
    quota = mapped_column(Integer, default=0)


class File(Base):
    __tablename__ = 'files'

    file_id = mapped_column(String, primary_key=True)
    filename = mapped_column(String)

    @property
    def filepath(self):
        if '.mp4' in self.filename:
            return BASE_DIR.joinpath('video').joinpath(self.filename)
        return BASE_DIR.joinpath('audio').joinpath(self.filename)

    async def exists(self):
        filepath = await aiofiles.ospath.exists(self.filepath)
        return bool(filepath)