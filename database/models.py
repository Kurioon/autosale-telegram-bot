from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer
from config import DB_URL

# Замінюємо старий шлях (sqlite+aiosqlite...) на змінну DB_URL
engine = create_async_engine(DB_URL, echo=True)

# Створюємо фабрику сесій (через неї ми будемо додавати та шукати авто)
async_session = async_sessionmaker(engine, expire_on_commit=False)

# Базовий клас для всіх таблиць
class Base(AsyncAttrs, DeclarativeBase):
    pass

# Описуємо таблицю автомобілів
class Car(Base):
    __tablename__ = 'cars'

    id: Mapped[int] = mapped_column(primary_key=True)
    make: Mapped[str] = mapped_column(String(50))           # Марка (напр., Toyota)
    model: Mapped[str] = mapped_column(String(50))          # Модель (напр., Camry)
    year: Mapped[int] = mapped_column()                     # Рік випуску
    engine_volume: Mapped[float] = mapped_column()          # Об'єм двигуна (напр., 2.5)
    fuel_type: Mapped[str] = mapped_column(String(50))      # Тип пального
    transmission: Mapped[str] = mapped_column(String(50))   # Коробка передач
    mileage: Mapped[int] = mapped_column()                  # Пробіг (у тис. км)
    price: Mapped[int] = mapped_column()                    # Ціна в доларах
    photo_id: Mapped[str] = mapped_column(String(255), nullable=True) # ID фотографії в Telegram
    channel_link: Mapped[str] = mapped_column(String(255), nullable=True) # Посилання на телеграм канал

# Функція для створення таблиць у базі даних
async def init_db():
    async with engine.begin() as conn:
        # Створюємо всі таблиці, які успадковані від Base
        await conn.run_sync(Base.metadata.create_all)