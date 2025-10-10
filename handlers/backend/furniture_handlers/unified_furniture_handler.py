from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
import re

from database.crud import CrudFurniture
from keyboard.button_template import contry_of_origin_kb, kitchen_subcategory_inline_kb
from keyboard.keyboard_builder import make_row_inline_keyboards
from settings import config
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


def extract_kitchen_type(description: str) -> tuple:
    match = re.search(r'\[(.*?)\]', description)
    if match:
        kitchen_type = match.group(1)
        clean_description = re.sub(r'\[.*?\]\s*', '', description)
        return kitchen_type, clean_description
    return None, description


async def show_furniture_list(message: types.Message, category_name: str, country: str = "🇷🇺 Россия", kitchen_type: str = None):
    crud = CrudFurniture()

    # Для кухонной мебели всегда используем Россию как страну
    if "кухонная" in category_name.lower():
        country = "🇷🇺 Россия"

    # Получаем все товары по категории и стране
    furniture_list = await crud.get_furniture_by_category_and_country(
        category_name=category_name,
        country=country
    )

    # Если указан тип кухни, фильтруем по нему
    if kitchen_type and furniture_list:
        furniture_list = [
            furniture for furniture in furniture_list
            if f"[{kitchen_type}]" in furniture.description
        ]

    # Контактная информация
    contact_info = (
        f"🪑 Для заказа мебели пишите нам:\n"
        f"📲 WhatsApp: https://wa.me/+{config.NUMBER}\n"
        f'💬 Telegram: https://t.me/{config.TELEGRAM}\n'
        f'{"-" * 50}\n'
        f"✨ Будьте в курсе новинок и акций!\n"
        "Подписывайтесь на нас в Instagram, чтобы не пропустить свежие коллекции и вдохновение для вашего дома:\n"
        f"📸 Instagram: https://instagram.com/{config.INSTAGRAM}\n"
        f'{"-" * 50}\n'
    )

    if furniture_list:
        for furniture in furniture_list:
            # Извлекаем тип кухни из описания для кухонной мебели
            displayed_kitchen_type = ""
            if "кухонная" in category_name.lower():
                kt, clean_description = extract_kitchen_type(furniture.description)
                if kt:
                    displayed_kitchen_type = f"🍳 Тип кухни: {kt}\n"
            else:
                clean_description = furniture.description

            furniture_text = (
                f"{clean_description}\n\n"
                f"{displayed_kitchen_type}"
                f"🏷️ Категория Мебели: {furniture.category_name}\n"
                f"🌍 Страна производства: {furniture.country_origin}\n"
                f"📆 Дата добавления: {furniture.created_at}\n\n\n"
                f"{'-' * 50}\n"
                f"{contact_info}"
            )

            # Отправляем фотографии
            photos = await crud.get_furniture_photos(furniture.id)
            if photos:
                media_group = [types.InputMediaPhoto(media=photo.file_id) for photo in photos[:10]]
                try:
                    await message.answer_media_group(media_group)
                except Exception:
                    for photo in photos[:10]:
                        await message.answer_photo(photo.file_id)
            else:
                await message.answer("📷 Фотографии отсутствуют")

            # Отправляем текстовое описание
            await message.answer(furniture_text, disable_web_page_preview=True)

    else:
        await message.answer("📭 Пока нет добавленой мебели по данной категории.")


@router.callback_query(F.data.in_(FURNITURE_NAMES.keys()))
async def furniture_callback(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик выбора типа мебели."""
    furniture_type = callback_query.data
    await state.update_data(type_furniture=furniture_type)

    if furniture_type in TYPES_WITH_SUBCATEGORIES:
        await callback_query.message.edit_text(
            "Выберите тип кухонной мебели:",
            reply_markup=make_row_inline_keyboards(kitchen_subcategory_inline_kb)
        )

    elif furniture_type in TYPES_WITH_ORIGIN:
        await callback_query.message.edit_text(
            "Отлично! Теперь выберите страну производства:",
            reply_markup=make_row_inline_keyboards(contry_of_origin_kb)
        )

    else:
        category_name = FURNITURE_NAMES.get(furniture_type, 'Спальная мебель')
        await show_furniture_list(callback_query.message, category_name)

    await callback_query.answer()


@router.callback_query(F.data.in_(KITCHEN_SUBCATEGORIES.keys()))
@router.callback_query(F.data == "back_to_main")
async def kitchen_subcategory_callback(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "back_to_main":
        await back_to_main_callback(callback_query, state)
    else:
        # Сохраняем выбранный тип кухни
        kitchen_type_key = callback_query.data
        kitchen_type = KITCHEN_SUBCATEGORIES.get(kitchen_type_key, 'Кухня')

        await state.update_data(kitchen_subcategory=kitchen_type_key)
        await state.update_data(selected_kitchen_type=kitchen_type)

        # Для кухонной мебели сразу показываем товары
        await show_furniture_list(
            callback_query.message,
            "🍳 Кухонная мебель",
            "🇷🇺 Россия",
            kitchen_type
        )

    await callback_query.answer()


@router.callback_query(F.data.in_(ORIGIN_NAMES.keys()))
async def origin_callback(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    furniture_type = user_data.get('type_furniture', 'sleep_furniture')
    origin_type = callback_query.data

    await state.update_data(origin_type=origin_type)

    category_name = FURNITURE_NAMES.get(furniture_type, 'Спальная мебель')
    origin_name = ORIGIN_NAMES.get(origin_type, '🇷🇺 Россия')
    kitchen_type = user_data.get('selected_kitchen_type')

    # Показываем мебель по выбранной категории, типу кухни и стране
    await show_furniture_list(callback_query.message, category_name, origin_name, kitchen_type)

    await callback_query.answer()
