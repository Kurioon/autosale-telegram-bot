from aiogram.fsm.state import State, StatesGroup

class FilterCar(StatesGroup):
    waiting_for_year_from = State()
    waiting_for_year_to = State()