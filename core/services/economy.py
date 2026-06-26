from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User

async def check_media_access(session: AsyncSession, tg_id: int, partner_id: int, current_media_count: int, media_type: str) -> bool:
    """
    Перевірка доступу хлопця до медіа дівчини.
    Безкоштовно: тільки перші 2 фото. Відео — платно відразу.
    """
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    partner = await session.scalar(select(User).where(User.tg_id == partner_id))
    
    if not user or not partner:
        return False
        
    # Якщо це дівчина (Бджола) або у хлопця є VIP-підписка, доступ повний
    if user.gender == "female" or user.trust_level >= 50:  # trust_level 50+ як маркер VIP
        return True
        
    # Для хлопців (Трутнів): відео платне відразу
    if media_type == "video":
        return False
        
    # Фото безкоштовні тільки перші дві штуки за діалог
    if media_type == "photo" and current_media_count <= 2:
        return True
        
    return False

async def buy_media_unlock(session: AsyncSession, tg_id: int, cost: int = 5) -> bool:
    """ Списання 'Меду' за розблокування прихованого фото/відео """
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if not user or user.honey_balance < cost:
        return False
        
    # Знімаємо коїни з балансу Трутня
    await session.execute(
        update(User).where(User.tg_id == tg_id).values(honey_balance=User.honey_balance - cost)
    )
    await session.commit()
    return True
