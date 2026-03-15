from aiogram import Router, F
from aiogram.types import Message

misc_router = Router()

# Відловлюємо натискання саме на кнопку "📞 Контакти"
@misc_router.message(F.text == "📞 Контакти")
async def show_contacts(message: Message):
    text = (
        "🏢 <b>Автомайданчик PashAuto</b>\n\n"
        '📍 <b>Адреса:</b> м. Ужгород, район Минай, вул. Карпатського Патруса (Орієнтир навпроти "Батерки")\n'
        "📞 <b>Телефон:</b> +38 (066) 040-95-32\n"
        "🕒 <b>Графік роботи:</b> Пн-Нд, 09:00 - 18:00\n\n"
        "<i>Звертайтеся, будемо раді допомогти з вибором авто!</i>"
    )
    await message.answer(text, parse_mode="HTML")