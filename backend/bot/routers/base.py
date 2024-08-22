from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, Message, WebAppInfo, KeyboardButton
from aiogram.utils.keyboard import KeyboardBuilder

from config import WEBAPP_URL

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    builder = KeyboardBuilder()
    builder.row(
        KeyboardButton(text='Open 👀', web_app=WebAppInfo(url=WEBAPP_URL))
    )

    await message.answer('🤖 Hello from telegram bot\nYou can test mini app by clicking the button', reply_markup=builder.as_markup())
