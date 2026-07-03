from aiogram import Router, F, types
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User

router = Router()

@router.callback_query(F.data.startswith("mod_approve_"))
async def handle_admin_approve(callback: types.CallbackQuery, session: AsyncSession):
    """ Адмін затвердив фото — відправляємо хлопцю в чат рулетки """
    await callback.answer("🟢 Затверджено")
    data = callback.data.split("_")
    
    # Структура: mod_approve_{from_user_id}_{partner_id}_{file_id}
    from_user_id = int(data[2])
    partner_id = int(data[3])
    file_id = data[4]
    
    try:
        # Доставляємо фотографію кінцевому отримувачу
        await callback.bot.send_photo(
            chat_id=partner_id,
            photo=file_id,
            caption="📸 Тобі надіслали фотографію 18+ (пройшла перевірку)."
        )
        # Оновлюємо текст в адмін-панелі, щоб ви бачили результат
        await callback.message.edit_caption(caption=callback.message.caption + "\n\n✅ **СТАТУС: ЗАТВЕРДЖЕНО**")
    except Exception as e:
        print(f"Помилка доставки затвердженого медіа: {e}")

@router.callback_query(F.data.startswith("mod_decline_"))
async def handle_admin_decline(callback: types.CallbackQuery, session: AsyncSession):
    """ Адмін відхилив фото — блокуємо (або кидаємо попередження) дівчині """
    await callback.answer("🔴 Заблоковано", show_alert=True)
    data = callback.data.split("_")
    
    from_user_id = int(data[2])
    
    try:
        # Сер, видаємо попередження або обнуляємо карму порушниці
        await session.execute(
            update(User).where(User.tg_id == from_user_id).values(honey_karma=0)
        )
        await session.commit()
        
        # Сповіщаємо порушницю
        await callback.bot.send_message(
            chat_id=from_user_id,
            text="🛑 Твоє фото не пройшло модерацію безпеки Вулика. Карму знижено!"
        )
        await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ **СТАТУС: ЗАБЛОКОВАНО (Карма 0)**")
    except Exception as e:
        print(f"Помилка при блокуванні контенту: {e}")
