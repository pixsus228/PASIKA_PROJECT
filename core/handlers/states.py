from aiogram.fsm.state import StatesGroup, State

class Registration(StatesGroup):
    name = State()
    age = State()
    gender = State()
    city = State()
    is_military = State()
    bio = State()    # додав стан для опису про себе
    photo = State()  # фінальний етап з медіа

class EditProfile(StatesGroup):
    media = State()
    city = State()
    is_military = State()
    bio = State()    # додав стан для редагування опису

class RouletteState(StatesGroup):
    searching = State() # стан пошуку співрозмовника
    in_chat = State()   # стан активного чату