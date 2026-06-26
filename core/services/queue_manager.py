from datetime import datetime

# Сер, ініціалізував оперативну чергу
active_queue = {}

async def add_to_queue(tg_id: int, birth_date, gender: str, age_category: str):
    """ Додав бджілку в оперативну пам'ять """
    active_queue[tg_id] = {
        "birth_date": birth_date,
        "gender": gender,
        "age_category": age_category
    }

async def remove_from_queue(tg_id: int):
    """ Видалив з черги при відключенні чи старті чату """
    if tg_id in active_queue:
        del active_queue[tg_id]

def calculate_exact_age(birth_date) -> int:
    """ Розрахунок віку без похибок """
    today = datetime.today().date()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

async def find_partner_match(tg_id: int):
    """ Реалізація вікових мостів та лімітів безпеки """
    if tg_id not in active_queue:
        return None

    my_data = active_queue[tg_id]
    my_age = calculate_exact_age(my_data["birth_date"])

    for partner_id, p_data in list(active_queue.items()):
        if partner_id == tg_id:
            continue

        p_age = calculate_exact_age(p_data["birth_date"])
        age_diff = abs(my_age - p_age)

        if age_diff > 5:
            continue

        if (p_age < 18 and my_age > 25) or (my_age < 18 and p_age > 25):
            continue

        if (my_data["age_category"] == "junior" and p_data["age_category"] == "adult") or \
           (p_data["age_category"] == "adult" and my_data["age_category"] == "junior"):
            continue

        return partner_id

    return None
