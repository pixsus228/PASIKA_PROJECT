import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from database.models import Base

# Підключаю нові сегментовані роутери (Протокол Single Responsibility)
from core.handlers.dating import common, registration, profile, search, roulette

load_dotenv()

# Використовую бойову базу pasika_final.db на LOSTVAYNE-LOQ
engine = create_async_engine('sqlite+aiosqlite:///data/pasika_final.db')
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def database_middleware(handler, event, data):
    async with async_session() as session:
        data['session'] = session
        return await handler(event, data)


async def main():
    logging.basicConfig(level=logging.INFO)

    # Створюю папку для бази, якщо вона відсутня
    if not os.path.exists('data'):
        os.makedirs('data')

    # Синхронізую моделі з базою
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    # Закріплюю меню команд біля скріпки для зручності Серія
    await bot.set_my_commands([
        types.BotCommand(command="start", description="🚀 Запустити Вулик"),
        types.BotCommand(command="profile", description="🐝 Моя Анкета"),
        types.BotCommand(command="search", description="🍯 Пошук бджілок")
    ])

    # Реєструю мідлварь та роутери в правильному порядку
    dp.update.middleware(database_middleware)

    # Реєструю роутери
    dp.include_router(common.router)
    dp.include_router(registration.router)
    dp.include_router(profile.router)
    dp.include_router(search.router)
    dp.include_router(roulette.router) # додав роутер рулетки

    print("✅ Сер, Екосистему ПАСІКА запущено за новою модульною архітектурою.")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())