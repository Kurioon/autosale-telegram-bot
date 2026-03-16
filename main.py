import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
import os
from aiohttp import web

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

# Проста функція, яка повертає текст "Bot is alive!" при переході за посиланням
async def handle(request):
    return web.Response(text="Bot is alive!")

# Функція запуску фонового веб-сервера
async def init_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render автоматично видає порт через змінні середовища
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    
    await init_db()
    
    # Запуск фонового веб-сервера для Render
    await init_web_server()

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