from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.filter_state import FilterCar
from database.requests import search_cars_by_filters
from config import ADMIN_IDS
from keyboards.inline import (
    get_filter_main_menu, get_price_menu, 
    get_fuel_menu, get_trans_menu, get_make_menu, 
    FilterCB, get_catalog_keyboard
)

filter_router = Router()
DEFAULT_PHOTO = "https://lightwidget.com/wp-content/uploads/local-file-not-found.png"

@filter_router.message(F.text == "🔍 Пошук за фільтрами")
async def start_filter_menu(message: Message, state: FSMContext):
    await state.clear()
    data = await state.get_data()
    await message.answer("Налаштуйте параметри пошуку:", reply_markup=get_filter_main_menu(data))

@filter_router.callback_query(FilterCB.filter(F.action == "set_make"))
async def open_make_menu(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=get_make_menu())

@filter_router.callback_query(FilterCB.filter(F.action == "set_price"))
async def open_price_menu(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=get_price_menu())

@filter_router.callback_query(FilterCB.filter(F.action == "set_fuel"))
async def open_fuel_menu(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=get_fuel_menu())

@filter_router.callback_query(FilterCB.filter(F.action == "set_trans"))
async def open_trans_menu(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=get_trans_menu())

@filter_router.callback_query(FilterCB.filter(F.action.in_(["make", "price", "fuel", "trans"])))
async def save_filter_value(call: CallbackQuery, callback_data: FilterCB, state: FSMContext):
    if callback_data.action == "make":
        await state.update_data(make=callback_data.value)
    elif callback_data.action == "price":
        await state.update_data(price_val=callback_data.value, price_name=callback_data.name)
    elif callback_data.action == "fuel":
        await state.update_data(fuel=callback_data.value)
    elif callback_data.action == "trans":
        await state.update_data(trans=callback_data.name, trans_val=callback_data.value)
        
    data = await state.get_data()
    await call.message.edit_text("Налаштуйте параметри пошуку:", reply_markup=get_filter_main_menu(data))

@filter_router.callback_query(FilterCB.filter(F.action == "back"))
async def back_to_main_menu(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.edit_reply_markup(reply_markup=get_filter_main_menu(data))

@filter_router.callback_query(FilterCB.filter(F.action == "cancel"))
async def close_filter_menu(call: CallbackQuery, state: FSMContext):
    # Очищаємо пам'ять (видаляємо всі обрані фільтри)
    await state.clear()
    # Видаляємо саме повідомлення з меню
    await call.message.delete()

@filter_router.callback_query(FilterCB.filter(F.action == "reset"))
async def reset_filters(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=get_filter_main_menu({}))

@filter_router.callback_query(FilterCB.filter(F.action == "set_year"))
async def ask_year_from(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введіть мінімальний рік випуску (наприклад: 2010):")
    await state.set_state(FilterCar.waiting_for_year_from)
    await call.answer()

@filter_router.message(FilterCar.waiting_for_year_from)
async def process_year_from(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Будь ласка, введіть число.")
    await state.update_data(year_from=int(message.text))
    await message.answer("Введіть максимальний рік випуску (наприклад: 2023):")
    await state.set_state(FilterCar.waiting_for_year_to)

@filter_router.message(FilterCar.waiting_for_year_to)
async def process_year_to(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Будь ласка, введіть число.")
    await state.update_data(year_to=int(message.text))
    data = await state.get_data()
    await message.answer("Рік збережено. Продовжуйте налаштування:", reply_markup=get_filter_main_menu(data))
    await state.set_state(None)

@filter_router.callback_query(FilterCB.filter(F.action == "search"))
async def execute_search(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cars = await search_cars_by_filters(data)
    
    await call.message.delete()
    
    if not cars:
        await call.message.answer("На жаль, за вашими критеріями нічого не знайдено 😔")
        return
    
    # Записуємо в пам'ять, що зараз працює фільтр
    await state.update_data(is_filtering=True)
    
    # Виводимо перше авто з каруселлю
    car = cars[0]
    is_admin = call.from_user.id in ADMIN_IDS
    
    text = (
        f"<b>{car.make} {car.model} ({car.year})</b>\n"
        f"💰 Ціна: {car.price}$\n\n"
        f"⚙️ Двигун: {car.engine_volume} л ({car.fuel_type})\n"
        f"🕹 Коробка: {car.transmission}\n"
        f"🛣 Пробіг: {car.mileage} тис. км"
    )
    if car.channel_link:
        text += f"\n\n👉 <b><a href='{car.channel_link}'>Більше фото та опис в каналі</a></b>"
    
    kb = get_catalog_keyboard(current_index=0, total_cars=len(cars), car_id=car.id, is_admin=is_admin)
    photo = car.photo_id if car.photo_id else DEFAULT_PHOTO
    
    await call.message.answer(f"✅ Знайдено {len(cars)} авто за вашими фільтрами:")
    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb, parse_mode="HTML")