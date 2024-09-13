from fastapi import Request
from pydantic import BaseModel
from datetime import datetime


class User(BaseModel):
    id: int
    username: str
    subscription_until: datetime


class WebAppRequest(Request):
    def __init__(self, webapp_user, **kwargs):
        self.__dict__.update(kwargs)
        self.webapp_user: User = webapp_user

class Video(BaseModel):
    chat_id: str
    video_path: str