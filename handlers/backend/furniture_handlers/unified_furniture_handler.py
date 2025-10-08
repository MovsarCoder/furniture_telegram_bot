"""
Унифицированный обработчик для всех типов мебели.
Заменяет отдельные обработчики для каждого типа мебели.
"""

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from database.crud import CrudFurniture
from keyboard.button_template import contry_of_origin_kb, kitchen_subcategory_kb, send_furnitures_buttons
from keyboard.keyboard_builder import make_row_inline_keyboards, make_row_keyboards
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


async def show_furniture_list(message: types.Message, category_name: str, country: str = "🇷🇺 Россия"):
    """
    Показывает список мебели по категории и стране производства.
    
    Args:
        message: Сообщение для ответа
        category_name: Название категории мебели
        country: Страна производства (по умолчанию Россия)
    """
    crud = CrudFurniture()
    furniture_list = await crud.get_furniture_by_category_and_country(
        category_name=category_name,
        country=country
    )
    number = ""
    telegram = ""
    instagram = ""
    text = (
        f"🪑 Для заказа мебели пишите нам:\n"
        f"📲 WhatsApp: https://wa.me/+{number}\n"
        f'💬 Telegram: https://t.me/{telegram}\n'
        f'{"-" * 50}\n'
        f"✨ Будьте в курсе новинок и акций!\n"
        "Подписывайтесь на нас в Instagram, чтобы не пропустить свежие коллекции и вдохновение для вашего дома:\n"
        f"📸 Instagram: https://instagram.com/{instagram}\n"
        f'{"-" * 50}\n'

    )

    if furniture_list:
        for furniture in furniture_list:
            await message.answer(
                f"🆔 ID: {furniture.id}\n"
                f"📝 Описание: {furniture.description}\n"
                f"🏷️ Категория Мебели: {furniture.category_name}\n"
                f"🌍 Страна производства: {furniture.country_origin}\n"
                f"📆 Дата добавления: {furniture.created_at}\n\n\n"
                f"{'-' * 50}\n"
                f"{text}",

                disable_web_page_preview=True, reply_markup=make_row_keyboards(send_furnitures_buttons))
    else:
        await message.answer("📭 Пока нет добавленой мебели по данной категории.")


@router.callback_query(F.data.in_(FURNITURE_NAMES.keys()))
async def furniture_callback(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик выбора типа мебели."""
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
        # Для остальных типов мебели сразу показываем мебель (страна по умолчанию - Россия)
        category_name = FURNITURE_NAMES.get(furniture_type, 'Спальная мебель')
        await show_furniture_list(callback_query.message, category_name)

    await callback_query.answer()


@router.callback_query(F.data.in_(KITCHEN_SUBCATEGORIES.keys()))
@router.callback_query(F.data == "back_to_main")
async def kitchen_subcategory_callback(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик выбора подкатегории кухонной мебели или возврата в главное меню."""
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


@router.callback_query(F.data.in_(ORIGIN_NAMES.keys()))
async def origin_callback(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик выбора страны производства."""
    # Получаем данные из состояния
    user_data = await state.get_data()
    furniture_type = user_data.get('type_furniture', 'sleep_furniture')
    origin_type = callback_query.data

    # Сохраняем выбранную страну производства
    await state.update_data(origin_type=origin_type)

    # Формируем сообщение с выбором пользователя
    category_name = FURNITURE_NAMES.get(furniture_type, 'Спальная мебель')
    origin_name = ORIGIN_NAMES.get(origin_type, '🇷🇺 Россия')

    # Показываем мебель по выбранной категории и стране
    await show_furniture_list(callback_query.message, category_name, origin_name)

    await callback_query.answer()
