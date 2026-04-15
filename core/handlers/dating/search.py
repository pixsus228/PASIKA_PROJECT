# (c) 2026 Olexiy Karnaukh. All rights reserved.
# LOSTVAYNE-CORE: Match Engine Module

import asyncio
import random
from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Match

router = Router()


async def get_universal_markup(user_id: int, current_index: int, total_media: int, is_own: bool):
    """Генератор універсальної клавіатури для навігації та взаємодії"""
    kb = InlineKeyboardBuilder()

    # Навігація між фото/відео, якщо їх більше одного
    if total_media > 1:
        prev_idx = (current_index - 1) % total_media
        next_idx = (current_index + 1) % total_media
        kb.row(
            types.InlineKeyboardButton(text="⬅️", callback_data=f"nav_{user_id}_{prev_idx}"),
            types.InlineKeyboardButton(text="➡️", callback_data=f"nav_{user_id}_{next_idx}")
        )

    # Кнопки дій залежно від того, чия це анкета
    if not is_own:
        kb.row(
            types.InlineKeyboardButton(text="👎", callback_data=f"dislike_{user_id}"),
            types.InlineKeyboardButton(text="❤️", callback_data=f"like_{user_id}")
        )
    else:
        kb.row(
            types.InlineKeyboardButton(text="🖼️ Медіа", callback_data="edit_media"),
            types.InlineKeyboardButton(text="📍 Місто", callback_data="edit_city")
        )
    return kb.as_markup()


@router.message(F.text == "🍯 Пошук")
async def cmd_search(message: types.Message, session: AsyncSession):
    """Пошук та вивід випадкової анкети"""
    target = await session.scalar(
        select(User).where(
            User.tg_id != message.from_user.id,
            User.age != None
        ).order_by(func.random()).limit(1)
    )

    if not target:
        return await message.answer("Поки що нових бджілок немає. 🐝")

    caption = (f"👤 {target.username}, {target.age}\n📍 {target.city}\n"
               f"🎖️ ЗСУ: {'Так' if target.is_military else 'Ні'}")

    markup = await get_universal_markup(target.tg_id, 0, len(target.media_content or []), False)

    if target.media_content:
        m = target.media_content[0]
        # Визначив метод відправки за типом файлу (photo/video)
        method = message.answer_photo if m['type'] == 'photo' else message.answer_video
        await method(m['file_id'], caption=caption, reply_markup=markup)
    else:
        await message.answer(caption, reply_markup=markup)


@router.callback_query(F.data.startswith("like_"))
async def handle_like(callback: types.CallbackQuery, session: AsyncSession):
    """Обробка симпатії та перевірка на взаємність"""
    target_tg_id = int(callback.data.split("_")[1])

    user = await session.scalar(select(User).where(User.tg_id == callback.from_user.id))
    target = await session.scalar(select(User).where(User.tg_id == target_tg_id))

    # Перевірив, чи є вже лайк від цієї людини до нас
    existing_like = await session.scalar(
        select(Match).where(
            and_(Match.from_user_id == target.id, Match.to_user_id == user.id)
        )
    )

    if existing_like:
        # Взаємний метч: оновив існуючий та записав новий
        existing_like.is_mutual = True
        session.add(Match(from_user_id=user.id, to_user_id=target.id, is_mutual=True))

        # Delayed Match: імітую людську паузу 2-5 хв перед сповіщенням
        delay = random.randint(120, 300)
        asyncio.create_task(send_match_notification(callback.bot, user.tg_id, target.tg_id, delay))
    else:
        # Просто запис про лайк
        session.add(Match(from_user_id=user.id, to_user_id=target.id))

    await session.commit()
    await callback.answer("Лайк відправлено! 🍯")
    await callback.message.delete()
    await cmd_search(callback.message, session)


@router.callback_query(F.data.startswith("dislike_"))
async def handle_dislike(callback: types.CallbackQuery, session: AsyncSession):
    """Пропуск анкети та перехід до наступної"""
    await callback.answer("Пропущено 💨")
    await callback.message.delete()
    await cmd_search(callback.message, session)


async def send_match_notification(bot, user_id, target_id, delay):
    """Фонова задача для відкладеного сповіщення про метч"""
    await asyncio.sleep(delay)
    text = "🐝 **У вас нова симпатія!** ❤️\nПеревірте розділ метчів."
    for uid in [user_id, target_id]:
        try:
            await bot.send_message(uid, text)
        except Exception:
            pass