from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import logging

# Налаштовую двигун з логуванням помилок
engine = create_async_engine('sqlite+aiosqlite:///data/pasika_final.db', echo=False)
session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def check_db_connection():
    try:
        async with engine.connect() as conn:
            logging.info("🐝 БД: З'єднання встановлено успішно.")
    except Exception as e:
        logging.error(f"❌ БД: Помилка з'єднання: {e}")
