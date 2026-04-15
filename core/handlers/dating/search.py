from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Match
from core.handlers.dating.common import get_main_kb

router = Router()


async def get_universal_markup(user_id: int, current_index: int, total_media: int, is_own: bool):
    kb = InlineKeyboardBuilder()
    if total_media > 1:
        prev_idx = current_index - 1 if current_index > 0 else total_media - 1
        next_idx = current_index + 1 if current_index < total_media - 1 else 0
        kb.row(
            types.InlineKeyboardButton(text="⬅️", callback_data=f"nav_{user_id}_{prev_idx}"),
            types.InlineKeyboardButton(text="➡️", callback_data=f"nav_{user_id}_{next_idx}")
        )
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
    target = await session.scalar(
        select(User).where(User.tg_id != message.from_user.id, User.age != None).order_by(func.random()).limit(1)
    )
    if not target:
        return await message.answer("Поки що нових бджілок немає. 🐝")

    markup = await get_universal_markup(target.tg_id, 0, len(target.media_content or []), False)
    # ... логіка виводу фото як у моноліті ...