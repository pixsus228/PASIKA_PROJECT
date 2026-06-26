import asyncio, logging, sys, os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from database.engine import session_maker
from core.middlewares.db import DbSessionMiddleware
from core.middlewares.antispam import ThrottlingMiddleware

# Роутери
from core.handlers.dating.common import router as common_router
from core.handlers.dating.registration import router as registration_router
from core.handlers.dating.roulette import router as roulette_router
from core.handlers.dating.gossip_wall import router as gossip_router
from core.handlers.dating.admin_moderation import router as admin_mod_router
from core.services.radar import router as radar_router
from core.services.economy import router as economy_router
from core.services.clans import router as clans_router
from core.services.profile_battle import router as battle_router

async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", stream=sys.stdout)
    bot = Bot(token=os.getenv("TOKEN"))
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))
    dp.update.middleware(ThrottlingMiddleware(limit=0.5))

    for router in [common_router, registration_router, roulette_router, gossip_router, admin_mod_router, radar_router, economy_router, clans_router, battle_router]:
        dp.include_router(router)

    logging.info("🐝 Вулик: Антиспам-щит активовано!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(main())
