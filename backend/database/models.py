import uuid

from sqlalchemy import BigInteger, String
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
