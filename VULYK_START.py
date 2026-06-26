import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.callback_answer import CallbackQueryMiddleware

# Імпорт конфігурації бази даних
from database.engine import session_maker
from core.middlewares.db import DbSessionMiddleware

# Сер, імпортую всі наші оновлені роутери
from core.handlers.dating.common import router as common_router
from core.handlers.dating.registration import router as registration_router
from core.handlers.dating.roulette import router as roulette_router
from core.handlers.dating.gossip_wall import router as gossip_router
from core.handlers.dating.admin_moderation import router as admin_mod_router

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )

    # Сер, завантажую токен безпечно (переконайся, що він є в .env)
    import os
    TOKEN = os.getenv("TOKEN")
    if not TOKEN:
        logging.critical("🛑 ТОКЕН БОТА НЕ ЗНАЙДЕНО В .env!")
        return

    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Підключаємо сесію бази даних через Middleware
    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))
    dp.callback_query.middleware(CallbackQueryMiddleware())

    # Реєстрація роутерів у суворому порядку
    dp.include_router(common_router)
    dp.include_router(registration_router)
    dp.include_router(roulette_router)
    dp.include_router(gossip_router)
    dp.include_router(admin_mod_router)

    logging.info("🐝 Вулик успішно запущено під нові стандарти LOSTVAYNE-CORE!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    from dotenv import load_file, load_dotenv
    load_dotenv()
    asyncio.run(main())
