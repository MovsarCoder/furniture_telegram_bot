from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from database.crud import CrudCategory, CrudFurniture
from keyboard.button_template import country_kb
from keyboard.keyboard_builder import make_row_keyboards
from states.states import NewFurnitureStates

router = Router()


@router.callback_query(F.data == 'new_furniture')
async def new_furniture_function(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.answer()

    text = (
        "🪄 <b>Добавление новой мебели</b>\n\n"
        "Пожалуйста, введите <b>описание</b> мебели — укажите её особенности, стиль или материал.\n\n"
        "Пример:\n<code>Элегантный кожаный диван с мягкой обивкой и прочным каркасом.</code>"
    )

    await callback_query.message.answer(text)
    await state.set_state(NewFurnitureStates.description)


@router.message(NewFurnitureStates.description)
async def get_description_new_furniture(message: types.Message, state: FSMContext):
    description_furniture = (message.text or '').strip()
    if not description_furniture:
        await message.answer("⚠️ Описание не может быть пустым. Пожалуйста, попробуйте снова.")
        return

    await state.update_data(description_new_furniture=description_furniture)

    crud = CrudCategory()
    get_categories = await crud.get_all_categories()
    categories = [category_name.name for category_name in get_categories]

    if not categories:
        await message.answer("📭 В базе пока нет категорий. Сначала создайте хотя бы одну категорию мебели.")
        await state.clear()
        return

    text = (
        "✨ Отлично!\n\n"
        "Теперь выберите <b>категорию</b> для этой мебели из списка ниже 👇"
    )

    await message.answer(text, reply_markup=make_row_keyboards(categories))
    await state.set_state(NewFurnitureStates.category)


@router.message(NewFurnitureStates.category)
async def get_category(message: types.Message, state: FSMContext):
    category_name = (message.text or '').strip()

    if not category_name:
        await message.answer("⚠️ Выберите категорию из предложенного списка.")
        return

    await state.update_data(category_name=category_name)

    text = (
        f"🗂 Категория выбрана: <b>{category_name}</b>\n\n"
        "Теперь укажите <b>страну происхождения</b> мебели 🌍\n"
        "Выберите из списка ниже:"
    )

    await message.answer(text, reply_markup=make_row_keyboards(country_kb))
    await state.set_state(NewFurnitureStates.country)


@router.message(NewFurnitureStates.country)
async def get_country(message: types.Message, state: FSMContext):
    country_name = (message.text or '').strip()

    if not country_name:
        await message.answer("⚠️ Пожалуйста, выберите страну из предложенного списка.")
        return

    data = await state.get_data()
    description = data.get("description_new_furniture", 'Нет описания')
    category_name = data.get("category_name", "Без категории")

    crud = CrudFurniture()
    new_furniture = await crud.create_furniture(
        description=description,
        category=category_name,
        country=country_name
    )

    if not new_furniture:
        await message.answer("❌ Произошла ошибка при сохранении мебели. Обратитесь к администратору.")
        return

    text = (
        "🎉 <b>Мебель успешно добавлена!</b>\n\n"
        f"<b>Категория:</b> {category_name}\n"
        f"<b>Страна:</b> {country_name}\n"
        f"<b>Описание:</b> {description}\n\n"
        "Спасибо за добавление! ✅"
    )

    await message.answer(text, reply_markup=types.ReplyKeyboardRemove())
    await state.clear()
