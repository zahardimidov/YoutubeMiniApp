from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, Message, WebAppInfo, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database.requests import get_todays_downloadings, get_user, get_plans
from config import WEBAPP_URL
from datetime import datetime

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[
        KeyboardButton(text='Искать  🚀', web_app=WebAppInfo(url=WEBAPP_URL)),
        KeyboardButton(text='Мой профиль 👤')
    ]])

    await message.answer('Привет! 👋\nЯ твой помощник в мире видео на <b>YouTube</b>!🎥\n\n✨ С моей помощью ты сможешь легко находить и <b>скачивать</b> интересующие тебя <b>видео в удобном формате</b>.\n\U0001F50E Просто открой страницу, нажав на кнопку ниже, и воспользуйся поиском, чтобы найти видео.\nГотов начать? Давай искать! 🚀', reply_markup=markup)

@router.message(F.text == 'Мой профиль 👤')
async def profile(message: Message):
    markup = await get_plans_kb()

    user = await get_user(user_id=message.from_user.id)
    e = 'не ' if user.subscription_until == None or user.subscription_until < datetime.now().date() else ''
            
    downloadings = await get_todays_downloadings(user_id=message.from_user.id)

    await message.answer(f'👤 {message.from_user.username}\n\U0001F4E5 Скачивания за день: {downloadings}\n\u2728 Подписка {e}активка', reply_markup=markup)


async def get_plans_kb():
    plans = await get_plans()
    kb = []

    for plan in plans:
        kb.append([InlineKeyboardButton(text = f'{plan.price} руб. / {plan.days} дней')])

    return InlineKeyboardMarkup(inline_keyboard=kb)