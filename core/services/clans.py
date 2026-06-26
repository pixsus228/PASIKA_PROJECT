from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User

async def create_clan(session: AsyncSession, owner_tg_id: int, clan_name: str, cost: int = 50) -> bool:
    """ Створення нового клану. Коштує 50 крапель 'Меду' """
    user = await session.scalar(select(User).where(User.tg_id == owner_tg_id))
    if not user or user.honey_balance < cost:
        return False  # Не вистачає коштів

    # Записуємо створення клану в JSON-прогрес власника
    progress = user.media_content if isinstance(user.media_content, dict) else {}
    if "clan" in progress:
        return False  # Вже є клан
        
    progress["clan"] = {"name": clan_name, "role": "leader", "members": [owner_tg_id]}
    
    await session.execute(
        update(User).where(User.tg_id == owner_tg_id).values(
            honey_balance=User.honey_balance - cost,
            media_content=progress
        )
    )
    await session.commit()
    return True

async def join_clan(session: AsyncSession, tg_id: int, clan_owner_tg_id: int) -> bool:
    """ Приєднання бджілки до існуючого клану """
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    owner = await session.scalar(select(User).where(User.tg_id == clan_owner_tg_id))
    
    if not user or not owner:
        return False
        
    owner_progress = owner.media_content if isinstance(owner.media_content, dict) else {}
    clan_data = owner_progress.get("clan")
    
    if not clan_data:
        return False
        
    # Додаємо учасника у список клану
    if tg_id not in clan_data["members"]:
        clan_data["members"].append(tg_id)
        
    owner_progress["clan"] = clan_data
    
    # Оновлюємо дані у лідера
    await session.execute(update(User).where(User.tg_id == clan_owner_tg_id).values(media_content=owner_progress))
    
    # Прописуємо мітку клану самому юзеру
    user_progress = user.media_content if isinstance(user.media_content, dict) else {}
    user_progress["clan"] = {"name": clan_data["name"], "role": "member", "leader_id": clan_owner_tg_id}
    await session.execute(update(User).where(User.tg_id == tg_id).values(media_content=user_progress))
    
    await session.commit()
    return True
