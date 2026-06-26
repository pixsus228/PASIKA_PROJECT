from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing import Callable, Dict, Any, Awaitable
import logging

class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data: Dict[str, Any]) -> Any:
        async with self.session_pool() as session:
            data['session'] = session
            try:
                return await handler(event, data)
            except Exception as e:
                logging.error(f"❌ Критична помилка БД під час виконання: {e}")
                raise e
