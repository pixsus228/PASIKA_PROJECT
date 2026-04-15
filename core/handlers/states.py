from aiogram.fsm.state import StatesGroup, State

class Registration(StatesGroup):
    name = State()
    age = State()
    gender = State()
    city = State()
    is_military = State()
    photo = State()

# Додав відсутній клас для редагування профілю
class EditProfile(StatesGroup):
    media = State()
    city = State()