from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User
from core.handlers.states import Registration, EditProfile
from core.handlers.dating.common import get_main_kb, get_ready_kb
from core.handlers.dating.search import get_universal_markup

router = Router()


@router.message(F.text == "🐝 Моя Анкета")
async def show_profile(message: types.Message, session: AsyncSession, state: FSMContext):
    # Отримую дані користувача з БД
    user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))

    if not user or user.age is None:
        await state.set_state(Registration.name)
        return await message.answer("Твоєї анкети ще немає. Як тебе звати?")

    # Додав відображення біо в текст анкети
    bio_text = f"\n\n📝 **Про себе:**\n{user.bio}" if user.bio else ""

    text = (f"🐝 **Твоя Анкета:**\n\n👤 {user.username}, {user.age}\n📍 {user.city}\n"
            f"🎖️ ЗСУ: {'Так' if user.is_military else 'Ні'}\n🍯 Баланс: {user.honey_balance} мед."
            f"{bio_text}")

    markup = await get_universal_markup(user.tg_id, 0, len(user.media_content or []), True)

    if user.media_content:
        m = user.media_content[0]
        method = message.answer_photo if m['type'] == 'photo' else message.answer_video
        await method(m['file_id'], caption=text, reply_markup=markup)
    else:
        await message.answer(text, reply_markup=markup)


# --- РЕДАГУВАННЯ ДАНИХ ---

@router.callback_query(F.data == "edit_city")
async def edit_city_start(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(EditProfile.city)
    await callback.message.answer("Напиши назву нового міста: 🏡")
    await callback.answer()


@router.message(EditProfile.city)
async def edit_city_manual(message: types.Message, state: FSMContext, session: AsyncSession):
    # Оновив місто з великої літери
    formatted_city = message.text.strip().title()
    await session.execute(update(User).where(User.tg_id == message.from_user.id).values(city=formatted_city))
    await session.commit()
    await state.clear()
    await message.answer(f"✅ Місто змінено на: {formatted_city}", reply_markup=get_main_kb())


@router.callback_query(F.data == "edit_bio")
async def edit_bio_start(callback: types.CallbackQuery, state: FSMContext):
    # Початок редагування БІО
    await state.set_state(EditProfile.bio)
    await callback.message.answer("Напиши нову історію про себе: ✍️")
    await callback.answer()


@router.message(EditProfile.bio)
async def edit_bio_manual(message: types.Message, state: FSMContext, session: AsyncSession):
    # Записав нове БІО в базу
    new_bio = message.text.strip()
    await session.execute(update(User).where(User.tg_id == message.from_user.id).values(bio=new_bio))
    await session.commit()
    await state.clear()
    await message.answer("✅ Твою історію оновлено у Вулику!", reply_markup=get_main_kb())


@router.callback_query(F.data == "edit_media")
async def edit_media_start(callback: types.CallbackQuery, state: FSMContext):
    # Очищення та запис нових медіа
    await state.set_state(EditProfile.media)
    await state.update_data(media_content=[])
    await callback.message.answer("📸 **Оновлення галереї**\nНадішли до 4-х нових фото/відео.",
                                  reply_markup=get_ready_kb())
    await callback.answer()