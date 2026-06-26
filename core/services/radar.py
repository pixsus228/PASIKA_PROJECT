import math
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """ Математичний розрахунок відстані в кілометрах між двома точками """
    R = 6371.0  # Радіус Землі в км
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

async def get_nearby_users(session: AsyncSession, user_lat: float, user_lon: float, max_dist_km: float = 5.0) -> list:
    """ Пошук бджілок у радіусі max_dist_km поруч із користувачем """
    # Витягуємо всіх активних юзерів з бази
    stmt = select(User).where(User.search_status == "active", User.is_banned == False)
    result = await session.scalars(stmt)
    all_users = result.all()
    
    nearby = []
    for user in all_users:
        # Сер, оскільки ми зберігаємо координати у JSON-прогресі, витягуємо їх безпечно
        progress = user.media_content if isinstance(user.media_content, dict) else {}
        coords = progress.get("location")  # Очікуємо структуру {"lat": float, "lon": float}
        
        if not coords:
            continue
            
        dist = calculate_distance(user_lat, user_lon, coords["lat"], coords["lon"])
        if dist <= max_dist_km:
            nearby.append({"user_id": user.tg_id, "username": user.username, "distance_km": round(dist, 2)})
            
    return sorted(nearby, key=lambda x: x["distance_km"])
