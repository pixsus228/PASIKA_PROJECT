# (c) 2026 Olexiy Karnaukh. All rights reserved.
# LOSTVAYNE-CORE: Roulette Anonymous Logic (Fixed Imports)

import asyncio
import random
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command  # ДОДАНО: Імпорт для обробки команд
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User
from core.handlers.states import EditProfile  # Тимчасово використовуємо наявні або RouletteState

router = Router()

# Для мінімуму використовуємо RouletteState, який ви додали в states.py
from core.handlers.states import Registration  # Як приклад, або ваш RouletteState


@router.message(F.text == "🎲 Рулетка")
async def start_roulette(message: types.Message, session: AsyncSession, state: FSMContext):
    """Пошук випадкового партнера для чату"""
    await message.answer("Шукаю вільну бджілку для анонімного чату... 🔍")

    # Вибір рандомного користувача через SQL (крім себе)
    target = await session.scalar(
        select(User).where(User.tg_id != message.from_user.id).order_by(func.random()).limit(1)
    )

    if not target:
        return await message.answer("Зараз у Вулику пусто. Спробуй пізніше! 🐝")

    # Встановлюємо стан чату (використовуйте RouletteState.in_chat, якщо він вже в states.py)
    # await state.set_state(RouletteState.in_chat)
    await state.update_data(partner_id=target.tg_id)

    await message.answer(
        f"Знайшов! Анонімне з'єднання встановлено. 💬\n\n"
        "Ваші повідомлення пересилаються партнеру.\n"
        "Щоб вийти, напиши: /stop"
    )


@router.message(Command("stop"))
async def stop_roulette(message: types.Message, state: FSMContext):
    """Вихід з чату"""
    await state.clear()
    await message.answer("Анонімний чат завершено. Повертаємось до Вулика! 🐝")


@router.message()
async def chat_bridge(message: types.Message, state: FSMContext, bot):
    """Пересилання повідомлень партнеру (Bridge)"""
    data = await state.get_data()
    partner_id = data.get('partner_id')

    # Якщо ми в стані чату і є ID партнера - пересилаємо
    if partner_id:
        try:
            await message.send_copy(chat_id=partner_id)
        except Exception:
            await message.answer("⚠️ Не вдалося надіслати повідомлення.")