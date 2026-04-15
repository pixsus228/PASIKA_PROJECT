# (c) 2026 Olexiy Karnaukh. All rights reserved.
# LOSTVAYNE-CORE: Full Search, Interaction & Editor Logic

import asyncio
import random
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Match
from core.handlers.states import EditProfile

router = Router()


async def get_universal_markup(user_id: int, current_index: int, total_media: int, is_own: bool):
    """Генератор клавіатури: Навігація + Редагування/Взаємодія"""
    kb = InlineKeyboardBuilder()

    # Навігація (стрілки)
    if total_media > 1:
        prev_idx = (current_index - 1) % total_media
        next_idx = (current_index + 1) % total_media
        kb.row(
            types.InlineKeyboardButton(text="⬅️", callback_data=f"nav_{user_id}_{prev_idx}"),
            types.InlineKeyboardButton(text="➡️", callback_data=f"nav_{user_id}_{next_idx}")
        )

    if is_own:
        # Кнопки редагування для власника
        kb.row(
            types.InlineKeyboardButton(text="🖼️ Медіа", callback_data="edit_media"),
            types.InlineKeyboardButton(text="📍 Місто", callback_data="edit_city")
        )
        kb.row(types.InlineKeyboardButton(text="📝 Про мене", callback_data="edit_bio"))
    else:
        # Кнопки для чужих анкет
        kb.row(
            types.InlineKeyboardButton(text="👎", callback_data=f"dislike_{user_id}"),
            types.InlineKeyboardButton(text="❤️", callback_data=f"like_{user_id}")
        )
    return kb.as_markup()


@router.message(F.text == "🍯 Пошук")
async def cmd_search(message: types.Message, session: AsyncSession):
    """Пошук з жорстким фільтром tg_id (не показувати себе)"""
    # 1. Пріоритет: Військові (крім вас)
    target = await session.scalar(
        select(User).where(
            User.tg_id != message.from_user.id,
            User.age.isnot(None),
            User.is_military == True
        ).order_by(func.random()).limit(1)
    )

    # 2. Загальний пошук (якщо військових крім вас немає)
    if not target:
        target = await session.scalar(
            select(User).where(
                User.tg_id != message.from_user.id,
                User.age.isnot(None)
            ).order_by(func.random()).limit(1)
        )

    if not target:
        return await message.answer("Поки що інших бджілок немає. 🐝")

    prefix = "🎖️ ПОБРАТИМ: " if target.is_military else ""
    bio_text = f"\n\n📝 {target.bio}" if target.bio else ""
    caption = (f"{prefix}{target.username}, {target.age}\n📍 {target.city}\n"
               f"🎖️ ЗСУ: {'Так' if target.is_military else 'Ні'}{bio_text}")

    markup = await get_universal_markup(target.tg_id, 0, len(target.media_content or []), False)

    if target.media_content:
        m = target.media_content[0]
        method = message.answer_photo if m['type'] == 'photo' else message.answer_video
        await method(m['file_id'], caption=caption, reply_markup=markup)
    else:
        await message.answer(caption, reply_markup=markup)


@router.callback_query(F.data.startswith("nav_"))
async def handle_nav(callback: types.CallbackQuery, session: AsyncSession):
    """Обробка перемикання фото"""
    await callback.answer()
    data = callback.data.split("_")
    target_id, current_idx = int(data[1]), int(data[2])
    is_own = (target_id == callback.from_user.id)

    target = await session.scalar(select(User).where(User.tg_id == target_id))
    if not target or not target.media_content: return

    markup = await get_universal_markup(target_id, current_idx, len(target.media_content), is_own)
    m = target.media_content[current_idx]
    media = types.InputMediaPhoto(media=m['file_id']) if m['type'] == 'photo' else types.InputMediaVideo(
        media=m['file_id'])

    try:
        await callback.message.edit_media(media=media, reply_markup=markup)
    except:
        pass


@router.callback_query(F.data.startswith("like_"))
async def handle_like(callback: types.CallbackQuery, session: AsyncSession):
    """Лайк та перевірка на взаємність"""
    target_tg_id = int(callback.data.split("_")[1])
    await callback.answer("❤️")

    user = await session.scalar(select(User).where(User.tg_id == callback.from_user.id))
    target = await session.scalar(select(User).where(User.tg_id == target_tg_id))

    if user and target:
        existing = await session.scalar(
            select(Match).where(and_(Match.from_user_id == target.id, Match.to_user_id == user.id)))
        if existing:
            existing.is_mutual = True
            session.add(Match(from_user_id=user.id, to_user_id=target.id, is_mutual=True))
            asyncio.create_task(notify_match(callback.bot, user.tg_id, target.tg_id))
        else:
            session.add(Match(from_user_id=user.id, to_user_id=target.id))
        await session.commit()

    await callback.message.delete()
    await cmd_search(callback.message, session)


@router.callback_query(F.data.startswith("dislike_"))
async def handle_dislike(callback: types.CallbackQuery, session: AsyncSession):
    """Дизлайк: миттєвий перехід до наступної анкети"""
    await callback.answer("💨")
    await callback.message.delete()
    await cmd_search(callback.message, session)


@router.callback_query(F.data == "edit_bio")
async def edit_bio_start(callback: types.CallbackQuery, state: FSMContext):
    """Початок редагування 'Про мене'"""
    await state.set_state(EditProfile.bio)
    await callback.message.answer("Напиши новий текст 'Про мене': ✍️")
    await callback.answer()


async def notify_match(bot, u1, u2):
    """Сповіщення про взаємність з паузою"""
    await asyncio.sleep(random.randint(120, 300))
    for uid in [u1, u2]:
        try:
            await bot.send_message(uid, "🐝 **Взаємна симпатія у Вулику!** ❤️")
        except:
            pass