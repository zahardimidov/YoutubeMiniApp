from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, Message, WebAppInfo, KeyboardButton

from config import WEBAPP_URL

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[
        KeyboardButton(text='Open 👀', web_app=WebAppInfo(url=WEBAPP_URL))
    ]])

    await message.answer('🤖 Hello from telegram bot\nYou can test mini app by clicking the button', reply_markup=markup)
