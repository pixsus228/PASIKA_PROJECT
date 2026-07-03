import random
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User

# Сер, сформував пул базових квестів для вулика
QUESTS_POOL = [
    {"id": "likes_10", "text": "Поставити 10 лайків у стрічці 🍯", "target": 10},
    {"id": "roulette_5", "text": "Провести 5 хвилин у чат-рулетці 🎲", "target": 5},
    {"id": "gift_1", "text": "Надіслати віртуальний подарунок 🎁", "target": 1},
    {"id": "view_stories", "text": "Переглянути 3 Гарячі Сторіз 🔥", "target": 3}
]

async def generate_daily_quests() -> list:
    """ Випадковий вибір 3-х квестів на день """
    return random.sample(QUESTS_POOL, 3)

async def update_quest_progress(session: AsyncSession, tg_id: int, quest_id: str, amount: int = 1):
    """ Оновлення прогресу квесту в базі даних """
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if not user:
        return

    # Сер, оскільки ми зберігаємо прогрес у JSON полі, витягуємо поточні дані
    # (Це рішення економить місце і не потребує додаткових таблиць)
    progress = user.media_content if isinstance(user.media_content, dict) else {}
    quests = progress.get("daily_quests", [])
    
    all_completed = True
    for q in quests:
        if q["id"] == quest_id:
            q["current"] = min(q["current"] + amount, q["target"])
            if q["current"] == q["target"]:
                q["completed"] = True
                
        if not q.get("completed", False):
            all_completed = False

    # Якщо всі квести дня закрито — нараховуємо VIP-бонус (trust_level = 50)
    if all_completed and quests:
        await session.execute(
            update(User).where(User.tg_id == tg_id).values(trust_level=50)
        )
        
    progress["daily_quests"] = quests
    await session.execute(
        update(User).where(User.tg_id == tg_id).values(media_content=progress)
    )
    await session.commit()
