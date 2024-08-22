import json

from aiogram import F, Router
from aiogram.types import (ContentType, InlineKeyboardButton, Message,
                           WebAppInfo)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import WEBAPP_URL

router = Router()


@router.message(F.content_type == ContentType.WEB_APP_DATA)
async def webapp_data(message: Message):
    await message.answer(json.dumps(message.web_app_data))
