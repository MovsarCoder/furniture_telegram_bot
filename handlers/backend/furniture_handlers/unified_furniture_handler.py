from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
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

# Константа для количества товаров на странице
ITEMS_PER_PAGE = 10


def extract_kitchen_type(description: str) -> tuple:
    match = re.search(r'\[(.*?)\]', description)
    if match:
        kitchen_type = match.group(1)
        clean_description = re.sub(r'\[.*?\]\s*', '', description)
        return kitchen_type, clean_description
    return None, description


async def show_furniture_list(message: types.Message, category_name: str, country: str = "🇷🇺 Россия", kitchen_type: str = None, page: int = 0):
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

    if not furniture_list:
        await message.answer("📭 Пока нет добавленой мебели по данной категории.")
        return

    # Пагинация
    total_items = len(furniture_list)
    start_index = page * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    paginated_furniture = furniture_list[start_index:end_index]

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

    # Отправляем товары на текущей странице
    for furniture in paginated_furniture:
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

    # Создаем кнопки пагинации
    keyboard_buttons = []

    # Кнопка "Еще" если есть еще товары
    if end_index < total_items:
        keyboard_buttons.append([types.KeyboardButton(text="Еще")])

    # Кнопка "Главное меню" всегда
    keyboard_buttons.append([types.KeyboardButton(text="🏠 Главное меню")])

    # Создаем клавиатуру
    reply_markup = types.ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True
    )

    # Сохраняем информацию о пагинации в состоянии
    await message.answer(
        f"Показано {start_index + 1}-{min(end_index, total_items)} из {total_items} товаров",
        reply_markup=reply_markup
    )


@router.callback_query(F.data.in_(FURNITURE_NAMES.keys()))
async def furniture_callback(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик выбора типа мебели."""

    furniture_type = callback_query.data
    await state.update_data(type_furniture=furniture_type)
    await state.update_data(current_page=0)  # Сброс пагинации

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
        await state.update_data(current_page=0)  # Сброс пагинации

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
    await state.update_data(current_page=0)  # Сброс пагинации

    category_name = FURNITURE_NAMES.get(furniture_type, 'Спальная мебель')
    origin_name = ORIGIN_NAMES.get(origin_type, '🇷🇺 Россия')
    kitchen_type = user_data.get('selected_kitchen_type')

    # Показываем мебель по выбранной категории, типу кухни и стране
    await show_furniture_list(callback_query.message, category_name, origin_name, kitchen_type)

    await callback_query.answer()


# Обработчик для кнопки "Еще"
@router.message(F.text == "Еще")
async def more_furniture_handler(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    # Получаем данные из состояния
    furniture_type = user_data.get('type_furniture', 'sleep_furniture')
    category_name = FURNITURE_NAMES.get(furniture_type, 'Спальная мебель')
    origin_type = user_data.get('origin_type')
    origin_name = ORIGIN_NAMES.get(origin_type, '🇷🇺 Россия') if origin_type else "🇷🇺 Россия"
    kitchen_type = user_data.get('selected_kitchen_type')
    current_page = user_data.get('current_page', 0)

    # Увеличиваем номер страницы
    new_page = current_page + 1
    await state.update_data(current_page=new_page)

    # Показываем следующую страницу
    await show_furniture_list(message, category_name, origin_name, kitchen_type, new_page)


# Обработчик для кнопки "🏠 Главное меню"
@router.message(F.text == "🏠 Главное меню")
async def main_menu_handler(message: types.Message, state: FSMContext):
    # Очищаем состояние
    await state.clear()

    # Показываем главное меню (логика из navigation_handler)
    welcome_text = (
        "Здравствуйте! 👋\n\n"
        "Добро пожаловать в магазин мебели — здесь вы легко найдёте и оформите заказ на мебель для "
        "всех комнат. Ниже — главное меню. Нажмите на категорию, чтобы посмотреть модели, задать вопрос "
        "или оформить мини-заказ.\n\n"
        "🔹 На каждом этапе кнопка «Назад» возвращает на предыдущий уровень.\n"
        "🔹 Для оформления заказа потребуется имя и телефон.\n\n"
        "Чем начнём? Выберите категорию из меню 👇"
    )

    from keyboard.button_template import start_kb
    from keyboard.keyboard_builder import make_row_inline_keyboards

    await message.answer(
        welcome_text,
        reply_markup=make_row_inline_keyboards(start_kb)
    )
