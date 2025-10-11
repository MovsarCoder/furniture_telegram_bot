import logging

from aiogram import Router, types, filters, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError

from keyboard.button_template import start_kb
from keyboard.keyboard_builder import make_row_inline_keyboards

from database.crud import UserCrud

router = Router()


@router.message(filters.Command("start"))
@router.message(F.text == "🏠 Главное меню")
async def start(message: types.Message, state: FSMContext):
    await state.clear()

    welcome_text = (
        "🌟 <b>Добро пожаловать в наш мебельный бот!</b> 🌟\n\n"
        "🛋️ Здесь вы найдете стильную и качественную мебель для любого интерьера.\n\n"
        "📂 <b>Наш каталог включает:</b>\n"
        "• Спальни и матрасы\n"
        "• Кухонные гарнитуры\n"
        "• Мягкую мебель\n"
        "• Столы и стулья\n"
        "• Тумбы и комоды\n"
        "• Шкафы-купе и гардеробные\n\n"
        "🛒 <b>Как сделать заказ:</b>\n"
        "1. Выберите категорию мебели\n"
        "2. Просмотрите модели\n"
        "3. Свяжитесь с нами для заказа\n\n"
        "💬 <i>Для оформления заказа потребуется ваше имя и номер телефона</i>\n"
        "🔄 <i>В любой момент можно вернуться в главное меню</i>\n\n"
        "👇 <b>Выберите категорию из меню ниже:</b>"
    )

    keyboard = start_kb
    telegram_id = message.from_user.id
    crud = UserCrud()

    try:
        added_user = await crud.add_user(
            telegram_id=telegram_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            is_admin=False,  # по умолчанию
        )
        if added_user:
            logging.info("✅ Пользователь %s успешно зарегистрирован.", telegram_id)
        else:
            logging.info("👤 Пользователь %s уже существует или не был создан.", telegram_id)

    except IntegrityError as ie:
        logging.exception("❌ IntegrityError при добавлении пользователя %s: %s", telegram_id, ie)

    except Exception as e:
        logging.exception("❌ Ошибка при добавлении пользователя %s: %s", telegram_id, e)

    user = await crud.get_user_by_telegram_id(message.from_user.id)

    if user.is_admin:
        keyboard = start_kb + [("⚙️Настройки бота", 'settings_bot')]
        await message.answer(
            text=welcome_text,
            reply_markup=make_row_inline_keyboards(keyboard))

    else:
        await message.answer(
            text=welcome_text,
            reply_markup=make_row_inline_keyboards(keyboard))
