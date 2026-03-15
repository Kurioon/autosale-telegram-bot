from sqlalchemy import select, delete # Додано імпорт delete
from database.models import async_session, Car

async def get_all_cars():
    async with async_session() as session:
        # Робимо запит до бази: "Вибрати все з таблиці Car"
        result = await session.execute(select(Car))
        # Повертаємо список всіх знайдених автомобілів
        return result.scalars().all()
    
async def search_cars_by_filters(filters: dict):
    async with async_session() as session:
        query = select(Car)
        
        # Фільтр по марці (НОВЕ)
        if 'make' in filters and filters['make'] != 'Всі':
            query = query.where(Car.make == filters['make'])
            
        # Фільтр по роках
        if 'year_from' in filters:
            query = query.where(Car.year >= filters['year_from'])
        if 'year_to' in filters:
            query = query.where(Car.year <= filters['year_to'])
            
        # Фільтр по ціні
        if 'price_val' in filters:
            min_p, max_p = map(int, filters['price_val'].split('-'))
            query = query.where(Car.price >= min_p, Car.price <= max_p)
            
        # Фільтр по паливу
        if 'fuel' in filters:
            query = query.where(Car.fuel_type == filters['fuel'])
            
        # Фільтр по коробці
        if 'trans_val' in filters:
            query = query.where(Car.transmission == filters['trans_val'])
            
        result = await session.execute(query)
        return result.scalars().all()

async def add_new_car(data: dict):
    async with async_session() as session:
        new_car = Car(
            make=data['make'],
            model=data['model'],
            year=data['year'],
            engine_volume=data['engine_volume'],
            fuel_type=data['fuel_type'],
            transmission=data['transmission'],
            mileage=data['mileage'],
            price=data['price'],
            photo_id=data['photo'], # Зберігаємо ID фотографії від Telegram
            channel_link=data.get('channel_link')
        
        )
        session.add(new_car)
        await session.commit()

async def delete_car(car_id: int):
    async with async_session() as session:
        # Видаляємо запис, де ID збігається з переданим
        await session.execute(delete(Car).where(Car.id == car_id))
        await session.commit()