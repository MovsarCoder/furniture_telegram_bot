import logging
from aiogram import F, Router, types

from keyboard.button_template import admin_kb, start_kb
from keyboard.keyboard_builder import make_row_inline_keyboards

router = Router()


@router.callback_query(F.data == 'settings_bot')
async def settings_bot(callback_query: types.CallbackQuery):
    await callback_query.answer("▶️")
    try:

        admin_text = (
            "🔧 <b>Панель администратора</b>\n\n"
            f"Здравствуйте, <b>{callback_query.from_user.full_name}</b> (<code>{callback_query.from_user.id}</code>)\n\n"
            "Выберите действие из меню ниже — кнопки аккуратно сгруппированы по задачам:\n\n"
        )

        if callback_query.message:
            try:
                await callback_query.message.edit_text(
                    text=admin_text,
                    reply_markup=make_row_inline_keyboards(admin_kb),
                )

            except Exception:
                await callback_query.message.answer(
                    text=admin_text,
                    reply_markup=make_row_inline_keyboards(admin_kb),
                )
        else:
            await callback_query.message.answer(
                text=admin_text,
                reply_markup=make_row_inline_keyboards(admin_kb),
            )

    except Exception as e:
        logging.exception("Ошибка в settings_bot callback: %s", e)
        await callback_query.message.answer("❌ Произошла ошибка при открытии админ-панели.")


@router.callback_query(F.data == 'back_to_main')
async def back_to_main(callback_query: types.CallbackQuery):
    await callback_query.answer("◀️")

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
    keyboard = start_kb + [("⚙️Настройки бота", 'settings_bot')]
    await callback_query.message.edit_text(text=welcome_text, reply_markup=make_row_inline_keyboards(keyboard))
