from aiogram import F, Router
from aiogram.types import ContentType, Message
from config import WEBAPP_URL

router = Router()


@router.message(F.content_type == ContentType.WEB_APP_DATA)
async def webapp_data(message: Message):
    print(message.web_app_data.data, type(message.web_app_data.data))
    await message.answer(str(message.web_app_data.data))
