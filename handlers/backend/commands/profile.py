from aiogram import Router, types, filters

router = Router()


@router.message(filters.Command('profile'))
async def profile(message: types.Message):
    await message.answer('Ваш профиль: ')


from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.crud import UserCrud

router = Router()


@router.message(Command("profile"))
async def profile_command(message: Message):
    telegram_id = message.from_user.id
    crud = UserCrud()
    user = await crud.get_user_by_telegram_id(telegram_id)

    if not user:
        await message.answer("🚫 Пользователь не найден в базе данных.")
        return

    # Данные пользователя
    user_id = f'{user.id}' if user.id else "-"
    username = f"@{user.username}" if user.username else "—"
    firstname = user.firstname or "—"
    lastname = user.lastname or "—"
    reg_date = user.registration_date.strftime("%d.%m.%Y %H:%M")
    is_admin = "✅ Да" if user.is_admin else "❌ Нет"

    # Профиль
    profile_text = (
        f"<b>👤 Профиль пользователя</b> {username}\n"
        f"<code>{'━' * 30}</code>\n"
        f"<b>🧾 Основное</b>\n"
        f"├ 🆔 ID: <code>{user_id}</code>\n"
        f"├ 📱 Telegram ID: <code>{telegram_id}</code>\n"
        f"├ 👤 Username: {username}\n"
        f"├ 🧑 Имя: {firstname}\n"
        f"├ 👨‍👩‍👧 Фамилия: {lastname}\n"
        f"├ 🗓 Зарегистрирован: {reg_date}\n"
        f"└ 🛡 Админ: {is_admin}\n"
    )

    await message.answer(profile_text)
