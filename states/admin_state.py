from aiogram.fsm.state import State, StatesGroup

class AddCar(StatesGroup):
    make = State()
    model = State()
    year = State()
    engine_volume = State()
    fuel_type = State()
    transmission = State()
    mileage = State()
    price = State()
    channel_link = State()
    photo = State()