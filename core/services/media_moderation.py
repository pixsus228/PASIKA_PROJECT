import os
from aiogram import Bot, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Сер, сюди прописуємо ID вашого адмін-акаунту або чату модерації з .env
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

async def send_to_admin_moderation(bot: Bot, from_user_id: int, partner_id: int, file_id: str, media_type: str = "photo"):
    """
    Тіньове перехоплення: надсилає фотографію дівчини адміну на перевірку.
    """
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(text="🟢 Затвердити", callback_data=f"mod_approve_{from_user_id}_{partner_id}_{file_id}"),
        types.InlineKeyboardButton(text="🔴 Заблокувати", callback_data=f"mod_decline_{from_user_id}_{partner_id}")
    )
    
    caption = f"🔔 **Модерація контенту 18+**\nВід: User TG `{from_user_id}`\nКому: User TG `{partner_id}`"
    
    try:
        if media_type == "photo":
            await bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=file_id, caption=caption, reply_markup=kb.as_markup())
        else:
            await bot.send_video(chat_id=ADMIN_CHAT_ID, video=file_id, caption=caption, reply_markup=kb.as_markup())
    except Exception as e:
        print(f"Помилка надсилання адміну на модерацію: {e}")
