from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🚗 Всі авто"),
                KeyboardButton(text="🔍 Пошук за фільтрами")
            ],
            [
                KeyboardButton(text="📞 Контакти")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Оберіть дію..."
    )
    return keyboard