from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from database.requests import get_all_cars, delete_car, search_cars_by_filters
from keyboards.inline import PaginationCB, DeleteCarCB, get_catalog_keyboard
from config import ADMIN_IDS

catalog_router = Router()
DEFAULT_PHOTO = "https://lightwidget.com/wp-content/uploads/local-file-not-found.png"

def format_car_text(car):
    text = (
        f"<b>{car.make} {car.model} ({car.year})</b>\n"
        f"💰 Ціна: {car.price}$\n\n"
        f"⚙️ Двигун: {car.engine_volume} л ({car.fuel_type})\n"
        f"🕹 Коробка: {car.transmission}\n"
        f"🛣 Пробіг: {car.mileage} тис. км"
    )
    # Якщо посилання існує, додаємо його в кінець тексту
    if car.channel_link:
        text += f"\n\n👉 <b><a href='{car.channel_link}'>Більше фото та опис в каналі</a></b>"
        
    return text

# 1. Запуск каталогу (всі авто)
@catalog_router.message(F.text == "🚗 Всі авто")
async def show_catalog(message: Message, state: FSMContext):
    # Скидаємо попередні фільтри, бо користувач захотів побачити всі авто
    await state.clear()
    await state.update_data(is_filtering=False)

    cars = await get_all_cars()
    if not cars:
        return await message.answer("Каталог автомобілів наразі порожній.")

    car = cars[0]
    is_admin = message.from_user.id in ADMIN_IDS
    text = format_car_text(car)
    kb = get_catalog_keyboard(current_index=0, total_cars=len(cars), car_id=car.id, is_admin=is_admin)
    photo = car.photo_id if car.photo_id else DEFAULT_PHOTO

    await message.answer_photo(photo=photo, caption=text, reply_markup=kb, parse_mode="HTML")

# 2. Обробка кнопок "Вперед/Назад"
@catalog_router.callback_query(PaginationCB.filter(F.action.in_(["prev", "next"])))
async def paginate_catalog(call: CallbackQuery, callback_data: PaginationCB, state: FSMContext):
    data = await state.get_data()
    
    # ПЕРЕВІРКА: ми гортаємо відфільтрований список чи всі авто?
    if data.get("is_filtering"):
        cars = await search_cars_by_filters(data)
    else:
        cars = await get_all_cars()

    if not cars:
        return await call.message.edit_text("Список порожній.")

    index = callback_data.index
    if index >= len(cars):
        index = 0

    car = cars[index]
    is_admin = call.from_user.id in ADMIN_IDS
    text = format_car_text(car)
    kb = get_catalog_keyboard(current_index=index, total_cars=len(cars), car_id=car.id, is_admin=is_admin)
    photo = car.photo_id if car.photo_id else DEFAULT_PHOTO

    media = InputMediaPhoto(media=photo, caption=text, parse_mode="HTML")
    await call.message.edit_media(media=media, reply_markup=kb)
    await call.answer()

# 3. Обробка кнопки "Видалити"
@catalog_router.callback_query(DeleteCarCB.filter())
async def delete_car_handler(call: CallbackQuery, callback_data: DeleteCarCB, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS:
        return await call.answer("У вас немає прав для цієї дії.", show_alert=True)

    await delete_car(callback_data.car_id)
    await call.answer("✅ Автомобіль успішно видалено!", show_alert=True)

    # Оновлюємо список після видалення (зберігаючи режим фільтрації)
    data = await state.get_data()
    if data.get("is_filtering"):
        cars = await search_cars_by_filters(data)
    else:
        cars = await get_all_cars()

    if not cars:
        await call.message.delete()
        await call.message.answer("Список порожній.")
        return

    car = cars[0]
    text = format_car_text(car)
    kb = get_catalog_keyboard(current_index=0, total_cars=len(cars), car_id=car.id, is_admin=True)
    photo = car.photo_id if car.photo_id else DEFAULT_PHOTO

    media = InputMediaPhoto(media=photo, caption=text, parse_mode="HTML")
    await call.message.edit_media(media=media, reply_markup=kb)