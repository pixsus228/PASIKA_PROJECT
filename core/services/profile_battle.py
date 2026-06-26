import random
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User

async def get_battle_pair(session: AsyncSession, category: str, gender: str) -> list:
    """
    Витягує дві випадкові активні анкети для дуелі 
    всередині однієї вікової соти та статі.
    """
    stmt = select(User).where(
        User.age_category == category,
        User.gender == gender,
        User.search_status == "active",
        User.is_banned == False
    )
    result = await session.scalars(stmt)
    users_list = list(result.all())
    
    if len(users_list) < 2:
        return []
        
    # Сер, обираємо 2 унікальні анкети з бази
    return random.sample(users_list, 2)

async def award_battle_winner(session: AsyncSession, winner_tg_id: int, reward_honey: int = 10):
    """ Нагородження переможця дуелі коїнами та підняття карми """
    await session.execute(
        update(User).where(User.tg_id == winner_tg_id).values(
            honey_balance=User.honey_balance + reward_honey,
            honey_karma=User.honey_karma + 5
        )
    )
    await session.commit()
