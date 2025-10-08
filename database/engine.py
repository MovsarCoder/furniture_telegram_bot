import os
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs

# Формируем абсолютный путь к базе данных
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Корень проекта
DB_PATH = os.path.join(BASE_DIR, 'database', 'database.db')

DATABASE_URL = f'sqlite+aiosqlite:///{DB_PATH}'

async_engine = create_async_engine(DATABASE_URL, echo=False, pool_size=10)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)


# Базовый класс для моделей
class Base(AsyncAttrs, DeclarativeBase):
    pass
