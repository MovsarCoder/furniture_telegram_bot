from aiogram.types import BotCommand

# 🎯 Основные команды бота
start_command = BotCommand(
    command='start',
    description='🚀 Перезапустить бота / Главное меню'
)

profile_command = BotCommand(
    command='profile',
    description='📊 Ваш профиль и статистика использования'
)

# 📋 Список всех команд
commands = [
    start_command,
    profile_command,
]
