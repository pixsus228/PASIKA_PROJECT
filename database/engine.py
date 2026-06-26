from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os

# Сер, використовуємо SQLite для нашого Вулика
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///data/pasika.db")

engine = create_async_engine(DATABASE_URL, echo=False)
session_maker = async_sessionmaker(engine, expire_on_commit=False)
