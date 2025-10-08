import logging
from typing import Optional, List

from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database.engine import AsyncSessionLocal
from database.models import User, Cooperation, Category, Furniture, FurniturePhoto


class UserCrud:
    def __init__(self):
        self.session = AsyncSessionLocal

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """
        Вернуть пользователя по telegram_id или None, если не найден.
        """
        async with self.session() as session:
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def add_user(
            self,
            telegram_id: int,
            username: Optional[str],
            first_name: Optional[str],
            last_name: Optional[str],
            is_admin: Optional[bool] = False,
    ) -> Optional[User]:
        """
        Добавляет пользователя, если его ещё нет.
        Возвращает созданный объект User при успехе, None при конфликте/ошибке.
        """
        try:
            # Сначала проверяем существование
            existing = await self.get_user_by_telegram_id(telegram_id)
            if existing:
                logging.warning("Пользователь с telegram_id=%s уже существует в базе.", telegram_id)
                return None

            # Открываем сессию и транзакцию
            async with self.session() as session:
                # Создаем объект модели
                new_user = User(
                    telegram_id=telegram_id,
                    username=username,
                    firstname=first_name,
                    lastname=last_name,
                    is_admin=bool(is_admin),
                )

                session.add(new_user)
                await session.commit()

                logging.info("Пользователь создан: telegram_id=%s username=%s", telegram_id, username)
                return new_user

        except IntegrityError as exc:
            # Ошибка целостности — возможен race condition или нарушение уникального ограничения
            logging.exception("IntegrityError при создании пользователя telegram_id=%s: %s", telegram_id, exc)
            return None

        except SQLAlchemyError as exc:
            # Общая ошибка sqlalchemy
            logging.exception("Database error при создании пользователя telegram_id=%s: %s", telegram_id, exc)
            return None

        except Exception as exc:
            # Неожиданная ошибка
            logging.exception("Неожиданная ошибка при add_user: %s", exc)
            return None


class CrudCooperation:
    def __init__(self):
        self.session = AsyncSessionLocal

    async def create_request(self,
                             telegram_id: int,
                             username: str,
                             text: str):
        async with self.session() as session:
            new_request = Cooperation(
                telegram_id=telegram_id,
                username=username,
                text_requests=text
            )

            session.add(new_request)
            await session.commit()
            await session.refresh(new_request)
            return new_request

    async def get_all_requests(self):
        async with self.session() as session:
            result = await session.execute(select(Cooperation))
            return result.scalars().all()

    async def get_requests_by_id(self, id):
        async with self.session() as session:
            stmt = select(Cooperation).where(Cooperation.id == id)
            get_requests = await session.execute(stmt)
            result = get_requests.scalar_one_or_none()
            return result

    async def cancel_request(self, request_id: int) -> bool:
        async with self.session() as session:
            stmt = delete(Cooperation).where(Cooperation.id == request_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def accept_request(self, request_id: int) -> bool:
        async with self.session() as session:
            stmt = delete(Cooperation).where(Cooperation.id == request_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0


class CrudCategory:
    def __init__(self):
        self.session = AsyncSessionLocal

    async def check_category_by_name(self, name: str) -> bool:
        if not name:
            return False

        async with self.session() as session:
            try:
                stmt = select(Category).where(Category.name == name)
                result = await session.execute(stmt)
                search_category = result.scalar_one_or_none()
                return search_category if search_category else None

            except SQLAlchemyError as exc:
                logging.exception("DB error in check_category_by_name: %s", exc)
                return False

    async def create_category(self, name: str, description: str) -> bool:
        if not name:
            logging.warning("create_category called with empty name")
            return False

        async with self.session() as session:
            try:
                new_cat = Category(name=name, description=description)
                session.add(new_cat)
                await session.commit()
                logging.info("Создана категория: %s", name)
                return True

            except IntegrityError as exc:
                await session.rollback()
                logging.error("IntegrityError при создании категории '%s': %s", name, exc)
                return False
            except SQLAlchemyError as exc:
                await session.rollback()
                logging.exception("SQLAlchemyError при создании категории '%s': %s", name, exc)
                return False
            except Exception as exc:
                await session.rollback()
                logging.exception("Неожиданная ошибка при создании категории '%s': %s", name, exc)
                return False

    async def get_all_categories(self) -> List[Category]:
        async with self.session() as session:

            try:
                stmt = select(Category)
                result = await session.execute(stmt)
                all_categories = result.scalars().all()
                return all_categories or []

            except SQLAlchemyError as exc:
                logging.exception("Ошибка при получении всех категорий: %s", exc)
                return []


class CrudFurniture:
    def __init__(self):
        self.session = AsyncSessionLocal

    async def create_furniture(
            self,
            description: str,
            category: str,
            country: str,
    ) -> Optional[Furniture]:
        """
        Создаёт запись Furniture и возвращает объект (или None при ошибке).
        Возврат объекта сохраняет совместимость с булевой проверкой (object -> True).
        """
        # Простейшая валидация/нормализация входных данных
        description = (description or "").strip()
        category = (category or "").strip()
        country = (country or "").strip()

        if not description:
            logging.warning("create_furniture called with empty description")
            return None

        if not category:
            logging.warning("create_furniture called with empty category")
            return None

        if not country:
            logging.warning("create_furniture called with empty country")
            return None

        async with self.session() as session:
            try:
                new_item = Furniture(
                    description=description,
                    category_name=category,
                    country_origin=country,
                )
                session.add(new_item)
                await session.commit()

                # Обновим объект из БД (получим id и прочие default-поля)
                try:
                    await session.refresh(new_item)
                except Exception:
                    # refresh не обязателен, но полезен; игнорируем если не поддерживается
                    logging.debug("session.refresh failed or not needed for Furniture")

                logging.info("Создана мебель: %s (id=%s)", description, getattr(new_item, "id", None))
                return new_item

            except SQLAlchemyError as exc:
                await session.rollback()
                logging.exception("DB error in create_furniture: %s", exc)
                return None

            except Exception as exc:
                await session.rollback()
                logging.exception("Unexpected error in create_furniture: %s", exc)
                return None

    async def get_furniture_by_category_and_country(self,
                                                    category_name: str,
                                                    country: str):
        async with self.session() as session:
            try:
                stmt = select(Furniture).where(
                    Furniture.category_name == category_name,
                    Furniture.country_origin == country
                )
                result = await session.execute(stmt)
                furniture = result.scalars().all()
                return furniture or None

            except SQLAlchemyError as exc:
                logging.exception("DB error in get_furniture_by_category_and_country: %s", exc)

    async def add_photos_to_furniture(self, furniture_id: int, photo_file_ids: List[str]) -> bool:
        """
        Добавляет фотографии к мебели.
        
        Args:
            furniture_id: ID мебели
            photo_file_ids: Список file_id фотографий из Telegram
            
        Returns:
            bool: True если успешно, False если ошибка
        """
        if not photo_file_ids:
            return False

        async with self.session() as session:
            try:
                # Создаем объекты фотографий
                photos = []
                for file_id in photo_file_ids:
                    photo = FurniturePhoto(
                        furniture_id=furniture_id,
                        file_id=file_id
                    )
                    photos.append(photo)

                # Добавляем все фотографии
                session.add_all(photos)
                await session.commit()
                logging.info("Добавлено %d фотографий к мебели с id=%s", len(photos), furniture_id)
                return True

            except SQLAlchemyError as exc:
                await session.rollback()
                logging.exception("DB error in add_photos_to_furniture: %s", exc)
                return False

            except Exception as exc:
                await session.rollback()
                logging.exception("Unexpected error in add_photos_to_furniture: %s", exc)
                return False

    async def get_furniture_photos(self, furniture_id: int) -> List[FurniturePhoto]:
        """
        Получает все фотографии для мебели.
        
        Args:
            furniture_id: ID мебели
            
        Returns:
            List[FurniturePhoto]: Список фотографий
        """
        async with self.session() as session:
            try:
                stmt = select(FurniturePhoto).where(FurniturePhoto.furniture_id == furniture_id)
                result = await session.execute(stmt)
                photos = result.scalars().all()
                return photos or []

            except SQLAlchemyError as exc:
                logging.exception("DB error in get_furniture_photos: %s", exc)
                return []