"""
Унифицированный обработчик для всех типов мебели.
Заменяет отдельные обработчики для каждого типа мебели.
"""

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from database.crud import CrudFurniture
from keyboard.button_template import contry_of_origin_kb, kitchen_subcategory_kb
from keyboard.keyboard_builder import make_row_inline_keyboards
from .navigation_handler import back_to_main_callback

router = Router()

# Словарь с названиями типов мебели
FURNITURE_NAMES = {
    'sleep_furniture': '🛏️ Спальная мебель',
    'kitchen_furniture': '🍳 Кухонная мебель',
    'soft_furniture': '🛋️ Мягкая мебель',
    'tables_chairs': '📚 Столы и стулья',
    'cabinets_commodes': '📺 Тумбы и комоды',
    'bed_furniture': '🛏️ Кровати',
    'mattresses': '🛏️️ Матрасы',
    'wardrobes': '🚪 Шкафы'
}

# Подкатегории кухонной мебели
KITCHEN_SUBCATEGORIES = {
    'straight_kitchen': '📏 Прямая кухня',
    'corner_kitchen': '📐 Угловая кухня'
}

# Словарь стран производства
ORIGIN_NAMES = {
    "russian_origin": "🇷🇺 Россия",
    "turkey_origin": "🇹🇷 Турция"
}

# Типы мебели, для которых нужно показывать страну производства
TYPES_WITH_ORIGIN = {'sleep_furniture', 'soft_furniture', 'tables_chairs'}

# Типы мебели, для которых есть подкатегории
TYPES_WITH_SUBCATEGORIES = {'kitchen_furniture'}


# Обработчик выбора типа мебели.
@router.callback_query(F.data.in_(FURNITURE_NAMES.keys()))
async def furniture_callback(callback_query: types.CallbackQuery, state: FSMContext):
    furniture_type = callback_query.data
    await state.update_data(type_furniture=furniture_type)

    # Если для этого типа мебели есть подкатегории
    if furniture_type in TYPES_WITH_SUBCATEGORIES:
        await callback_query.message.edit_text(
            "Выберите тип кухонной мебели:",
            reply_markup=make_row_inline_keyboards(kitchen_subcategory_kb)
        )

    # Если для этого типа мебели нужно показывать страну производства
    elif furniture_type in TYPES_WITH_ORIGIN:
        await callback_query.message.edit_text(
            "Отлично! Теперь выберите страну производства:",
            reply_markup=make_row_inline_keyboards(contry_of_origin_kb)
        )

    else:
        # Для остальных типов мебели показываем сообщение о скором доступе
        furniture_name = FURNITURE_NAMES.get(furniture_type, 'Мебель')
        print(furniture_name)
        crud = CrudFurniture()
        get_furniture = await crud.get_furniture_by_category_and_country(category_name=furniture_name, country="🇷🇺 Россия")
        if get_furniture:
            for i in get_furniture:
                await callback_query.message.answer(f"{i.id} | {i.description} | {i.category_name} | {i.country_origin}")
        else:
            await callback_query.message.answer("📭 Пока нет добавленой мебели по данной категории.")

    await callback_query.answer()


# Обработчик выбора подкатегории кухонной мебели или возврата в главное меню.
@router.callback_query(F.data.in_(KITCHEN_SUBCATEGORIES.keys()))
@router.callback_query(F.data == "back_to_main")
async def kitchen_subcategory_callback(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "back_to_main":
        await back_to_main_callback(callback_query, state)

    else:
        # Выбрана подкатегория кухонной мебели
        subcategory = callback_query.data
        subcategory_name = KITCHEN_SUBCATEGORIES.get(subcategory, 'Кухня')

        # Сохраняем подкатегорию
        await state.update_data(kitchen_subcategory=subcategory)

        await callback_query.message.edit_text(
            f"Вы выбрали: {subcategory_name}\n\n"
            "Скоро будет доступно!"
        )

    await callback_query.answer()


# Обработчик выбора страны производства.
@router.callback_query(F.data.in_(ORIGIN_NAMES.keys()))
async def origin_callback(callback_query: types.CallbackQuery, state: FSMContext):
    # Получаем данные из состояния
    user_data = await state.get_data()
    furniture_type = user_data.get('type_furniture', 'sleep_furniture')

    origin_type = callback_query.data

    # Сохраняем выбранную страну производства
    await state.update_data(origin_type=origin_type)

    # Формируем сообщение с выбором пользователя
    furniture_name = FURNITURE_NAMES.get(furniture_type, 'Неизвестный тип мебели')
    origin_name = ORIGIN_NAMES.get(origin_type, 'Неизвестная страна')

    crud = CrudFurniture()
    get_furniture = await crud.get_furniture_by_category_and_country(category_name=furniture_name, country=origin_name)

    if get_furniture:
        for i in get_furniture:
            await callback_query.message.answer(f"{i.id} | {i.description} | {i.category_name} | {i.country_origin}")
    else:
        await callback_query.message.answer("📭 Пока нет добавленой мебели по данной категории.")

    # await callback_query.message.answer(
    #     f"Ваш выбор:\n"
    #     f"• Тип мебели: {furniture_name}\n"
    #     f"• Страна производства: {origin_name}\n\n"
    #     "Скоро будет доступно!"
    # )

    await callback_query.answer()
