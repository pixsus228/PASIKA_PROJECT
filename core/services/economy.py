from aiogram import Router
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User
from sqlalchemy import update

router = Router()

async def add_honey(session: AsyncSession, tg_id: int, amount: int):
    """ Додавання меду на баланс """
    await session.execute(
        update(User).where(User.tg_id == tg_id).values(honey_balance=User.honey_balance + amount)
    )
    await session.commit()
