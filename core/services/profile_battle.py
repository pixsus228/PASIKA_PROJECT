from aiogram import Router
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User
from sqlalchemy import select, func

router = Router()

async def get_top_profile(session: AsyncSession):
    """ Визначення лідера дня за рейтингом """
    stmt = select(User).order_by(User.honey_balance.desc()).limit(1)
    result = await session.execute(stmt)
    return result.scalar()
