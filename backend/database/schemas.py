from fastapi import Request
from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str


class WebAppRequest(Request):
    def __init__(self, webapp_user, **kwargs):
        self.__dict__.update(kwargs)
        self.webapp_user: User = webapp_user
