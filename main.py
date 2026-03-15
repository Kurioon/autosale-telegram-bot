import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from config import BOT_TOKEN
from database.models import init_db
from keyboards.reply import get_main_menu
from handlers.catalog import catalog_router
from handlers.admin import admin_router
from handlers.filters import filter_router
from handlers.misc import misc_router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def handle_start(message: types.Message):
    # Тут ми додаємо reply_markup, який викликає появу кнопок
    await message.answer(
        f"Вітаю, {message.from_user.first_name}! 👋\n\n"
        f"Це бот для пошуку автомобілів. Оберіть дію в меню нижче:",
        reply_markup=get_main_menu()
    )

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    
    await init_db()
    
    # Підключаємо роутер з каталогом
    dp.include_router(catalog_router)
    dp.include_router(filter_router)
    dp.include_router(admin_router)
    dp.include_router(misc_router)
    
    print("Бот успішно запущений!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бота зупинено.")