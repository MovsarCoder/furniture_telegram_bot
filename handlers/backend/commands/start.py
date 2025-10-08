import logging

from aiogram import Router, types, filters, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError

from keyboard.button_template import start_kb
from keyboard.keyboard_builder import make_row_inline_keyboards

from database.crud import UserCrud

router = Router()


@router.message(filters.Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()

    welcome_text = (
        "Добро пожаловать! 🛋️\n\n"
        "Найдите идеальную мебель для любого уголка вашего дома.\n\n"
        "Просто выберите категорию ниже:\n"
        "• Посмотрите каталог моделей.\n"
        "• Получите информацию.\n"
        "• Оформите быстрый заказ.\n\n"
        "🔄 В любой момент можно вернуться «Назад».\n"
        "📞 Для завершения заказа потребуется ваше имя и телефон.\n\n"
        "Выбирайте, с чего начнём? 👇"
    )

    keyboard = start_kb
    telegram_id = message.from_user.id
    crud = UserCrud()

    # Попытка зарегистрировать пользователя — add_user должен быть idempotent (не падать при повторной вставке)
    try:
        # Ожидаем асинхронную операцию
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
