import os
from dotenv import load_dotenv

# Завантажуємо змінні з файлу .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Отримуємо рядок з ID, розбиваємо по комі і перетворюємо в список чисел
admin_ids_str = os.getenv("ADMIN_IDS", "")
# Якщо список порожній, помилки не буде
ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]

if not BOT_TOKEN:
    raise ValueError("Змінна BOT_TOKEN не знайдена у файлі .env!")