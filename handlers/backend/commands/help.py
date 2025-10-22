from aiogram import Router, filters, types


router = Router()


@router.message(filters.Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("Работает!!!!!")

