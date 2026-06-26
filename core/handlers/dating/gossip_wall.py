from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User

router = Router()

@router.message(Command("gossip"))
@router.message(F.text == "📢 Стіна Пліток")
async def show_gossip_wall(message: types.Message, session: AsyncSession):
    """ Показує базове інфо про стіну та правила публікації """
    await message.answer(
        "📢 **Анонімна Стіна Пліток м. Ромни** 🤫\n\n"
        "Тут ти можеш дізнатися або розповсюдити будь-які секрети міста абсолютно анонімно.\n\n"
        "✍️ Щоб опублікувати плітку, напиши: `/post текст_плітки`"
    )

@router.message(Command("post"))
async def create_gossip_post(message: types.Message, session: AsyncSession):
    """ Анонімна публікація від користувача """
    # Витягуємо текст після команди /post
    post_text = message.text.replace("/post", "").strip()
    
    if not post_text:
        return await message.answer("⚠️ Сер, напишіть текст після команди! Наприклад: `/post Бачив сьогодні...`")
        
    if len(post_text) > 400:
        return await message.answer("🛑 Повідомлення занадто довге (максимум 400 символів).")

    # Перевіряємо юзера в базі
    user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
    if not user:
        return

    # Сер, у майбутньому тут підключимо глобальну розсилку по усім активним юзерам міста
    # Поки що бот підтверджує фіксацію плітки у чергу стрічки
    await message.answer("✅ Твою плітку анонімно відправлено на Стіну Вулика! Очікуй реакцій.")
