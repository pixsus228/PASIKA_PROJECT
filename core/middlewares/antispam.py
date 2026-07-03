from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
import time

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit=1.0):
        self.limit = limit
        self.users = {}

    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data: Dict[str, Any]) -> Any:
        user_id = event.from_user.id
        now = time.time()
        if user_id in self.users and now - self.users[user_id] < self.limit:
            return await event.answer("🐝 Не так швидко! Почекай трохи.")
        self.users[user_id] = now
        return await handler(event, data)
