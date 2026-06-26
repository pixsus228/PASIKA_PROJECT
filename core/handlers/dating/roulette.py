from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from core.services.queue_manager import add_to_queue, remove_from_queue, find_partner_match
from core.services.antispam import is_spam_or_leak

router = Router()

@router.message(Command("roulette"))
@router.message(F.text == "🎲 Рулетка")
async def cmd_roulette_start(message: types.Message, session: AsyncSession, state: FSMContext):
    user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
    
    if not user or user.age is None:
        return await message.answer("⚠️ Сер, спочатку потрібно створити анкету в меню!")

    await add_to_queue(
        tg_id=user.tg_id,
        birth_date=user.birth_date,
        gender=user.gender,
        age_category=user.age_category
    )
    
    await message.answer("🔍 Шукаю вільну бджілку за твоїми віковими сотами... \nДля виходу напиши /stop або кнопку меню.")

    partner_id = await find_partner_match(user.tg_id)
    
    if partner_id:
        await remove_from_queue(user.tg_id)
        await remove_from_queue(partner_id)
        
        await state.update_data(in_chat_with=partner_id)
        
        await message.answer("🐝 Метч! З'єднання встановлено. Спілкуйтеся анонімно. Напиши /stop для виходу.")
        await message.bot.send_message(partner_id, "🐝 Метч! З'єднання встановлено. Спілкуйтеся анонімно. Напиши /stop для виходу.")
    return

@router.message(Command("stop"))
async def cmd_roulette_stop(message: types.Message, state: FSMContext):
    data = await state.get_data()
    partner_id = data.get("in_chat_with")
    
    await remove_from_queue(message.from_user.id)
    
    if partner_id:
        try:
            await message.bot.send_message(partner_id, "🛑 Співрозмовник завершив діалог. Повертаємось у вулик.")
        except:
            pass
        
    await state.clear()
    await message.answer("🛑 Діалог завершено. Ти повернувся до головного меню Вулика.")
    return

@router.message(F.text)
async def handle_roulette_chat(message: types.Message, state: FSMContext):
    data = await state.get_data()
    partner_id = data.get("in_chat_with")
    
    if not partner_id:
        return

    # Сер, перевіряю текст на наявність лінків/телефонів перед доставкою партнера
    if await is_spam_or_leak(message.text):
        return await message.answer("🛑 Сервіс безпеки: Обмін контактами (посилання, юзернейми, номери) заборонено! Спілкуйтеся всередині Вулика.")

    try:
        await message.copy_to(chat_id=partner_id)
    except Exception as e:
        print(f"Помилка доставки тексту: {e}")
