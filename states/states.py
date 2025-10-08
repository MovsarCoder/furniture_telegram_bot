from aiogram.fsm.state import StatesGroup, State


class CooperationStates(StatesGroup):
    text_requests = State()


class NewCategoryStates(StatesGroup):
    name_category = State()
    description_category = State()
