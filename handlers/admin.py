from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from filters.admin_filter import IsAdmin
from states.admin_state import AddCar
from database.requests import add_new_car

admin_router = Router()

# Цей хендлер спрацює тільки якщо користувач написав /add_car І він є в ADMIN_IDS
@admin_router.message(Command("add_car"), IsAdmin())
async def start_add_car(message: Message, state: FSMContext):
    await message.answer("🛠 Режим адміністратора: Додавання авто.\n\nВведіть марку (наприклад, Volkswagen):")
    await state.set_state(AddCar.make)

@admin_router.message(AddCar.make, IsAdmin())
async def add_make(message: Message, state: FSMContext):
    await state.update_data(make=message.text)
    await message.answer("Введіть модель (наприклад, Passat):")
    await state.set_state(AddCar.model)

@admin_router.message(AddCar.model, IsAdmin())
async def add_model(message: Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.answer("Введіть рік випуску (наприклад, 2018):")
    await state.set_state(AddCar.year)

@admin_router.message(AddCar.year, IsAdmin())
async def add_year(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Помилка! Введіть рік числом (наприклад, 2018):")
    await state.update_data(year=int(message.text))
    await message.answer("Введіть об'єм двигуна (наприклад, 2.0). Якщо електро — 0:")
    await state.set_state(AddCar.engine_volume)

@admin_router.message(AddCar.engine_volume, IsAdmin())
async def add_engine(message: Message, state: FSMContext):
    try:
        volume = float(message.text.replace(',', '.'))
        await state.update_data(engine_volume=volume)
    except ValueError:
        return await message.answer("Помилка! Введіть об'єм числом (наприклад, 2.0):")
    
    await message.answer("Введіть тип пального (Бензин, Дизель, Електро, Газ/Бензин):")
    await state.set_state(AddCar.fuel_type)

@admin_router.message(AddCar.fuel_type, IsAdmin())
async def add_fuel(message: Message, state: FSMContext):
    await state.update_data(fuel_type=message.text)
    await message.answer("Введіть коробку передач (Автомат, Механіка):")
    await state.set_state(AddCar.transmission)

@admin_router.message(AddCar.transmission, IsAdmin())
async def add_trans(message: Message, state: FSMContext):
    await state.update_data(transmission=message.text)
    await message.answer("Введіть пробіг у тис. км (наприклад, 150):")
    await state.set_state(AddCar.mileage)

@admin_router.message(AddCar.mileage, IsAdmin())
async def add_mileage(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Помилка! Введіть числом:")
    await state.update_data(mileage=int(message.text))
    await message.answer("Введіть ціну в $ (наприклад, 12500):")
    await state.set_state(AddCar.price)

@admin_router.message(AddCar.price, IsAdmin())
async def add_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Помилка! Введіть ціну числом:")
    await state.update_data(price=int(message.text))
    
    # Запитуємо посилання
    await message.answer("Введіть посилання на пост у Telegram-каналі.\nЯкщо посилання немає, надішліть знак мінус « - » :")
    await state.set_state(AddCar.channel_link)

# НОВИЙ ОБРОБНИК ДЛЯ ПОСИЛАННЯ
@admin_router.message(AddCar.channel_link, IsAdmin())
async def add_link(message: Message, state: FSMContext):
    # Якщо відправили "-", зберігаємо як порожнечу (None), інакше зберігаємо текст
    link = None if message.text.strip() == '-' else message.text
    await state.update_data(channel_link=link)
    
    await message.answer("📸 І останнє: відправте ОДНЕ фото автомобіля.")
    await state.set_state(AddCar.photo)

# Обробка ФОТОГРАФІЇ
@admin_router.message(AddCar.photo, IsAdmin(), F.photo)
async def add_photo(message: Message, state: FSMContext):
    # Telegram відправляє фото в кількох розмірах. Беремо найбільший (останній в масиві)
    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)
    
    data = await state.get_data()
    
    # Зберігаємо в базу
    await add_new_car(data)
    
    await message.answer(f"✅ Авто {data['make']} {data['model']} успішно додано до бази!")
    await state.clear()

# Якщо на останньому кроці відправили текст замість фото
@admin_router.message(AddCar.photo, IsAdmin())
async def add_photo_error(message: Message):
    await message.answer("Будь ласка, відправте саме фотографію, а не текст або файл.")