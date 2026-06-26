from aiogram import Router
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User
from sqlalchemy import update, select

router = Router()

# Сер, поки працюємо в RAM, але готуємо базу для постійного зберігання
clans = {} 

async def create_clan(session: AsyncSession, leader_tg_id: int, clan_name: str):
    """ Реєстрація клану в системі """
    clans[clan_name] = {"leader": leader_tg_id, "members": [leader_tg_id]}
    return True
