import random
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User

async def process_date_auction(session: AsyncSession, girl_id: int, top_bidder_id: int, final_bid: int):
    """ Аукціон побачень: бот списує ставку, забирає 20% комісії, решту віддає дівчині """
    fee = int(final_bid * 0.20)
    girl_share = final_bid - fee
    
    # Списуємо баланс у хлопця
    await session.execute(
        update(User).where(User.tg_id == top_bidder_id).values(honey_balance=User.honey_balance - final_bid)
    )
    # Нараховуємо дівчині її частку
    await session.execute(
        update(User).where(User.tg_id == girl_id).values(honey_balance=User.honey_balance + girl_share)
    )
    await session.commit()
