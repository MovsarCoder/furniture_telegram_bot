from aiogram.fsm.state import StatesGroup, State


class CooperationStates(StatesGroup):
    text_requests = State()


class NewCategoryStates(StatesGroup):
    name_category = State()
    description_category = State()


class NewFurnitureStates(StatesGroup):
    description = State()
    category = State()
    country = State()
    photos = State()  # Новое состояние для загрузки фотографий