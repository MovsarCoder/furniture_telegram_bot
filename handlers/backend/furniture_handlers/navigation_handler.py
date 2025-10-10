"""
Обработчик навигации для мебельного бота.
"""

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from keyboard.button_template import start_kb
from keyboard.keyboard_builder import make_row_inline_keyboards

router = Router()


@router.callback_query(F.data == "back_to_main")
async def back_to_main_callback(callback_query: types.CallbackQuery, state: FSMContext):
    """Возврат в главное меню."""
    # Очищаем состояние
    await state.clear()
    
    # Показываем главное меню
    welcome_text = (
        "Здравствуйте! 👋\n\n"
        "Добро пожаловать в магазин мебели — здесь вы легко найдёте и оформите заказ на мебель для "
        "всех комнат. Ниже — главное меню. Нажмите на категорию, чтобы посмотреть модели, задать вопрос "
        "или оформить мини-заказ.\n\n"
        "🔹 На каждом этапе кнопка «Назад» возвращает на предыдущий уровень.\n"
        "🔹 Для оформления заказа потребуется имя и телефон.\n\n"
        "Чем начнём? Выберите категорию из меню 👇"
    )
    
    await callback_query.message.edit_text(
        welcome_text,
        reply_markup=make_row_inline_keyboards(start_kb)
    )
    await callback_query.answer()