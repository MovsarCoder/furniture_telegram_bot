import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.methods import DeleteWebhook
from aiogram.types import BotCommandScopeAllPrivateChats

from keyboard.default_keyboard import commands
from settings.config import ConfigBot
from handlers import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)


async def main():
    bot = Bot(token=ConfigBot.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Подключение всех роутеров
    dp.include_router(router)

    # Удаление всех старый вебхуков
    await bot(DeleteWebhook(drop_pending_updates=True))

    # Подключение базовой менюшки со всеми командами
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllPrivateChats())

    # Запуск бота
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except TelegramBadRequest as e:
        logging.error(f"Telegram API error: {e}")
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.critical(f"Критическая ошибка: {e}", exc_info=True)
