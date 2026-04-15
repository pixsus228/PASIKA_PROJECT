import re
from datetime import datetime
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User
from core.handlers.states import Registration, EditProfile
from core.handlers.dating.common import get_back_kb, get_ready_kb, get_main_kb

router = Router()

# --- ПРОЦЕС РЕЄСТРАЦІЇ ---

@router.message(Registration.name)
async def reg_name(message: types.Message, state: FSMContext):
    # Зберіг ім'я, перевів на вік
    await state.update_data(name=message.text)
    await state.set_state(Registration.age)
    await message.answer(f"Приємно познайомитись! 😊\nНапиши дату народження (ДД.ММ.РРРР):", reply_markup=get_back_kb())

@router.message(Registration.age)
async def reg_age(message: types.Message, state: FSMContext):
    # Перевірив формат та вік 18+
    if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", message.text):
        return await message.answer("🛑 Формат: ДД.ММ.РРРР (напр. 04.12.2000) 📅")
    try:
        birth = datetime.strptime(message.text, "%d.%m.%Y")
        age = datetime.today().year - birth.year - (
                (datetime.today().month, datetime.today().day) < (birth.month, birth.day))
        if age < 18: return await message.answer("🔞 Вхід тільки 18+.")

        await state.update_data(age=age)
        await state.set_state(Registration.gender)

        kb = InlineKeyboardBuilder()
        kb.row(types.InlineKeyboardButton(text="Трутень (Ч) 🐝", callback_data="male"),
               types.InlineKeyboardButton(text="Бджола (Ж) 🌸", callback_data="female"))
        await message.answer(f"Твій вік: {age}. Обери стать:", reply_markup=kb.as_markup())
    except ValueError:
        await message.answer("⚠️ Дата некоректна.")

@router.callback_query(F.data.in_(["male", "female"]))
async def reg_gender(callback: types.CallbackQuery, state: FSMContext):
    # Записав стать, перейшов до міста
    await state.update_data(gender=callback.data)
    await state.set_state(Registration.city)
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="📍 Ромни", callback_data="city_romny"),
           types.InlineKeyboardButton(text="🌍 Інше місто", callback_data="city_manual"))
    await callback.message.edit_text("Звідки ти? 🏡", reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("city_"))
async def reg_city_select(callback: types.CallbackQuery, state: FSMContext):
    # Обробка вибору міста
    if callback.data == "city_romny":
        await state.update_data(city="Ромни")
        await ask_military(callback.message, state)
    else:
        await callback.message.answer("Напиши назву свого міста ✍️")
    await callback.answer()

@router.message(Registration.city)
async def reg_city_manual(message: types.Message, state: FSMContext):
    # Форматував місто з великої літери
    formatted_city = message.text.strip().title()
    await state.update_data(city=formatted_city)
    await ask_military(message, state)

async def ask_military(message: types.Message, state: FSMContext):
    # Питання про службу
    await state.set_state(Registration.is_military)
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="Так 🎖️", callback_data="mil_yes"),
           types.InlineKeyboardButton(text="Ні 🐝", callback_data="mil_no"))
    await message.answer("Ти в ЗСУ? 🎖️", reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("mil_"))
async def reg_military(callback: types.CallbackQuery, state: FSMContext):
    # Встановив стан Біо
    await state.update_data(is_military=(callback.data == "mil_yes"))
    await state.set_state(Registration.bio)
    await callback.message.answer("Розкажи трохи про себе (чим займаєшся, що шукаєш): ✍️")
    await callback.answer()

@router.message(Registration.bio)
async def reg_bio(message: types.Message, state: FSMContext):
    # Записав опис, перевів на медіа
    await state.update_data(bio=message.text)
    await state.set_state(Registration.photo)
    await message.answer("Супер! Тепер надішли до 4-х фото/відео. Тисни 'Готово'.", reply_markup=get_ready_kb())

# --- УНІВЕРСАЛЬНИЙ ОБРОБНИК МЕДІА ---

@router.message(Registration.photo, F.photo | F.video | F.text.casefold().contains("готово"))
@router.message(EditProfile.media, F.photo | F.video | F.text.casefold().contains("готово"))
async def media_process(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    media = data.get('media_content', [])

    if message.text and "готово" in message.text.lower():
        if not media:
            return await message.answer("Сер, додайте хоча б одне фото! 📸")

        update_data = {"media_content": media}

        # Фіналізація: зберігаю всі поля, включаючи bio
        current_state = await state.get_state()
        if current_state == Registration.photo:
            update_data.update({
                "username": data.get('name'),
                "age": data.get('age'),
                "gender": data.get('gender'),
                "city": data.get('city'),
                "is_military": data.get('is_military'),
                "bio": data.get('bio')
            })

        await session.execute(update(User).where(User.tg_id == message.from_user.id).values(**update_data))
        await session.commit()
        await state.clear()
        return await message.answer("✅ Дані збережено у Вулику!", reply_markup=get_main_kb())

    if len(media) < 4:
        # Зберіг медіафайл
        fid = message.photo[-1].file_id if message.photo else message.video.file_id
        media.append({"type": "photo" if message.photo else "video", "file_id": fid})
        await state.update_data(media_content=media)
        await message.answer(f"Додано ({len(media)}/4). Ще?", reply_markup=get_ready_kb())
    else:
        await message.answer("Ліміт вичерпано. Тисни '✅ Готово'.")