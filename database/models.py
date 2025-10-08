from datetime import datetime, timezone, timedelta
from uuid import uuid4

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text

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
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    in_stock = Column(Boolean, default=True, nullable=False)
    country_origin = Column(String, nullable=True)  # Страна производства (RU, TR и т.д.)
    created_at = Column(DateTime, default=lambda: datetime.now())

    def __repr__(self):
        return f"<Furniture(id={self.id}, name='{self.name}', price={self.price})>"


class Cooperation(Base):
    __tablename__ = 'cooperation_requests'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    username = Column(String, nullable=False)
    text_requests = Column(String, nullable=False)
    request_created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=3))))

    def __repr__(self):
        return f'{self.id} | {self.telegram_id} | {self.username} | {self.telegram_id} | {self.request_created_at}'
