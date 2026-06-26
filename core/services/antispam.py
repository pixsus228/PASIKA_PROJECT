import re
from aiogram import types

# Регулярні вирази для пошуку посилань, юзернеймів та мобільних номерів
URL_PATTERN = re.compile(r'(https?://[^\s]+|www\.[^\s]+|[a-zA- Senator].\.(me|com|org|net|biz|co|info|ua|ru))', re.IGNORECASE)
USERNAME_PATTERN = re.compile(r'@[a-zA-Z0-9_]{4,}', re.IGNORECASE)
PHONE_PATTERN = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{2,4}[-.\s]?\d{2,4}')

async def is_spam_or_leak(text: str) -> bool:
    """ Перевірка тексту на наявність контактів для запобігання витоку з Вулика """
    if not text:
        return False
        
    # Перевіряємо посилання, собачки месенджерів та цифри телефонів
    if URL_PATTERN.search(text) or USERNAME_PATTERN.search(text) or PHONE_PATTERN.search(text):
        return True
        
    return False
