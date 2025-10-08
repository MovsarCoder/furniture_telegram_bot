from aiogram import Router, F, types

router = Router()


@router.callback_query(F.data == 'soft_furniture')
async def sleep_furniture_callback(callback_query: types.CallbackQuery):
    await callback_query.answer("Скоро будет доступно: ")
