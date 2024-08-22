from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

from database.requests import get_user, set_user


class RegisterUserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str: Any],
    ) -> Any:

        if not event.chat.type == 'private':
            return

        user = await get_user(user_id=event.from_user.id)

        if not user:
            if not event.from_user.username:
                return await event.answer('⚙︎ Укажите username в настройках профиля, чтобы пользоваться ботом')

            user = await set_user(user_id=event.from_user.id, username=event.from_user.username)

        data['user'] = user

        return await handler(event, data)
