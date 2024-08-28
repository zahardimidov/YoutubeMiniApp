import uuid

from sqlalchemy import BigInteger, Date, Integer, String
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
    downloadings = mapped_column(Integer, default=0)


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
