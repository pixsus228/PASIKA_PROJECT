import re

# Сер, очищений та валідний патерн для виявлення посилань та контактів
URL_PATTERN = re.compile(r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.(me|com|org|net|biz|co|info|ua|ru))', re.IGNORECASE)

async def is_spam_or_leak(text: str) -> bool:
    """ Перевірка тексту на наявність посилань, юзернеймів або контактів """
    if not text:
        return False
    
    # Шукаємо посилання
    if URL_PATTERN.search(text):
        return True
        
    # Шукаємо згадки юзернеймів (@username) або телефони
    if re.search(r'(@\w+|(\+?\d{9,15}))', text):
        return True
        
    return False
