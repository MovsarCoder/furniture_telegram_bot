from datetime import datetime, timezone, timedelta
from uuid import uuid4

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from .engine import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    registration_date = Column(DateTime, default=lambda: datetime.now())
    is_admin = Column(Boolean, default=False, nullable=False)


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now())

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class Furniture(Base):
    __tablename__ = 'furniture'

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=True)
    category_name = Column(String, ForeignKey('categories.name'), nullable=False)
    country_origin = Column(String, nullable=True)  # Страна производства (RU, TR и т.д.)
    created_at = Column(DateTime, default=lambda: datetime.now())
    
    # Связь с фотографиями
    photos = relationship("FurniturePhoto", back_populates="furniture", cascade="all, delete-orphan")


class FurniturePhoto(Base):
    __tablename__ = 'furniture_photos'

    id = Column(Integer, primary_key=True, index=True)
    furniture_id = Column(Integer, ForeignKey('furniture.id'), nullable=False)
    file_id = Column(String, nullable=False)  # ID файла в Telegram
    file_path = Column(String, nullable=True)  # Путь к файлу (опционально)
    created_at = Column(DateTime, default=lambda: datetime.now())
    
    # Связь с мебелью
    furniture = relationship("Furniture", back_populates="photos")


class Cooperation(Base):
    __tablename__ = 'cooperation_requests'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    username = Column(String, nullable=False)
    text_requests = Column(String, nullable=False)
    request_created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=3))))

    def __repr__(self):
        return f'{self.id} | {self.telegram_id} | {self.username} | {self.telegram_id} | {self.request_created_at}'