from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

# --- КЛАСИ ДЛЯ ФІЛЬТРІВ ---
class FilterCB(CallbackData, prefix="flt"):
    action: str
    value: str = ""
    name: str = ""

# --- КЛАСИ ДЛЯ КАРУСЕЛІ ТА ВИДАЛЕННЯ ---
class PaginationCB(CallbackData, prefix="pag"):
    action: str
    index: int

class DeleteCarCB(CallbackData, prefix="del"):
    car_id: int


# ==========================================
# КЛАВІАТУРИ ДЛЯ КАРУСЕЛІ (КАТАЛОГУ)
# ==========================================
def get_catalog_keyboard(current_index: int, total_cars: int, car_id: int, is_admin: bool):
    builder = InlineKeyboardBuilder()

    prev_index = current_index - 1 if current_index > 0 else total_cars - 1
    next_index = current_index + 1 if current_index < total_cars - 1 else 0

    builder.button(text="⬅️", callback_data=PaginationCB(action="prev", index=prev_index))
    builder.button(text=f"{current_index + 1} / {total_cars}", callback_data=PaginationCB(action="ignore", index=current_index))
    builder.button(text="➡️", callback_data=PaginationCB(action="next", index=next_index))

    if is_admin:
        builder.button(text="🗑 Видалити", callback_data=DeleteCarCB(car_id=car_id))

    builder.adjust(3, 1)
    return builder.as_markup()


# ==========================================
# КЛАВІАТУРИ ДЛЯ ФІЛЬТРІВ
# ==========================================
def get_filter_main_menu(data: dict):
    builder = InlineKeyboardBuilder()
    
    make = data.get('make', 'Всі')
    y_from = data.get('year_from', '...')
    y_to = data.get('year_to', '...')
    price = data.get('price_name', 'Всі')
    fuel = data.get('fuel', 'Всі')
    trans = data.get('trans', 'Всі')

    builder.button(text=f"🚗 Марка: {make}", callback_data=FilterCB(action="set_make"))
    builder.button(text=f"📅 Рік: від {y_from} до {y_to}", callback_data=FilterCB(action="set_year"))
    builder.button(text=f"💰 Ціна: {price}", callback_data=FilterCB(action="set_price"))
    builder.button(text=f"⛽ Паливо: {fuel}", callback_data=FilterCB(action="set_fuel"))
    builder.button(text=f"🕹 Коробка: {trans}", callback_data=FilterCB(action="set_trans"))
    builder.button(text="❌ Скинути", callback_data=FilterCB(action="reset"))
    builder.button(text="🔎 ПОШУК", callback_data=FilterCB(action="search"))
    builder.button(text="🚪 Закрити", callback_data=FilterCB(action="cancel"))
    
    builder.adjust(1)
    return builder.as_markup()

def get_make_menu():
    builder = InlineKeyboardBuilder()
    makes = ["Volkswagen", "Skoda", "BMW", "Audi", "Opel", "Renault", "Ford", "KIA"]
    
    for m in makes:
        builder.button(text=m, callback_data=FilterCB(action="make", value=m, name=m))
        
    builder.button(text="Всі марки", callback_data=FilterCB(action="make", value="Всі", name="Всі"))
    builder.button(text="⬅️ Назад", callback_data=FilterCB(action="back"))
    
    builder.adjust(2) 
    return builder.as_markup()

def get_price_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="2000$ - 7000$", callback_data=FilterCB(action="price", value="2000-7000", name="2000$-7000$"))
    builder.button(text="7000$ - 12000$", callback_data=FilterCB(action="price", value="7000-12000", name="7000$-12000$"))
    builder.button(text="12000$ - 15000$", callback_data=FilterCB(action="price", value="12000-15000", name="12000$-15000$"))
    builder.button(text="15000$ - 20000$", callback_data=FilterCB(action="price", value="15000-20000", name="15000$-20000$"))
    builder.button(text="Більше 20000$", callback_data=FilterCB(action="price", value="20000-999999", name=">20000$"))
    builder.button(text="⬅️ Назад", callback_data=FilterCB(action="back"))
    builder.adjust(1)
    return builder.as_markup()

def get_fuel_menu():
    builder = InlineKeyboardBuilder()
    for f in ["Бензин", "Дизель", "Електро", "Газ/Бензин"]:
        builder.button(text=f, callback_data=FilterCB(action="fuel", value=f, name=f))
    builder.button(text="⬅️ Назад", callback_data=FilterCB(action="back"))
    builder.adjust(2, 2, 1) 
    return builder.as_markup()

def get_trans_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="Автомат", callback_data=FilterCB(action="trans", value="Автомат", name="Автомат"))
    builder.button(text="Механіка", callback_data=FilterCB(action="trans", value="Ручна", name="Механіка"))
    builder.button(text="⬅️ Назад", callback_data=FilterCB(action="back"))
    builder.adjust(2, 1)
    return builder.as_markup()