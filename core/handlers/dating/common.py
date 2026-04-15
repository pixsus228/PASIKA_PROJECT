from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User
from core.handlers.states import Registration

router = Router()

# --- КЛАВІАТУРИ ---

def get_main_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🐝 Моя Анкета"), types.KeyboardButton(text="🍯 Пошук"))
    builder.row(types.KeyboardButton(text="🎲 Рулетка"), types.KeyboardButton(text="🎖️ ЗСУ Хаб"))
    return builder.as_markup(resize_keyboard=True, is_persistent=True)

def get_back_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🔙 Головне меню"))
    return builder.as_markup(resize_keyboard=True)

def get_ready_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="✅ Готово"))
    builder.row(types.KeyboardButton(text="🔙 Головне меню"))
    return builder.as_markup(resize_keyboard=True)

# --- БАЗОВІ КОМАНДИ ---

@router.message(CommandStart())
async def cmd_start(message: types.Message, session: AsyncSession, state: FSMContext):
    user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
    if not user:
        session.add(User(tg_id=message.from_user.id, username=message.from_user.username))
        await session.commit()
        await state.set_state(Registration.name)
        return await message.answer("Привіт! 🐝 Давай створимо анкету. Як тебе звати?", reply_markup=get_back_kb())
    await message.answer(f"З поверненням, {user.username or 'бджілко'}! 🍯", reply_markup=get_main_kb())

@router.message(F.text == "🔙 Головне меню")
async def back_to_main(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Повертаємось до Вулика 🐝", reply_markup=get_main_kb())