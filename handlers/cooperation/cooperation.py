from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from database.crud import CrudCooperation
from keyboard.button_template import cancel_cooperation, start_kb
from keyboard.keyboard_builder import make_row_inline_keyboards
from states.states import CooperationStates

router = Router()


@router.callback_query(F.data == 'cooperation_company')
async def start_cooperation_application(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()

    await callback_query.message.answer(
        "📩 Пожалуйста, опишите ваше предложение по сотрудничеству.\n"
        "Мы внимательно рассмотрим каждую заявку. После отправки вам ответят в ближайшее время.",
        reply_markup=make_row_inline_keyboards(cancel_cooperation)
    )

    await state.set_state(CooperationStates.text_requests)


@router.message(CooperationStates.text_requests, F.text)
async def receive_cooperation_text(message: types.Message, state: FSMContext):
    get_text = message.text
    create_requests = await CrudCooperation().create_request(
        message.from_user.id,
        message.from_user.username,
        get_text
    )

    if create_requests:
        await message.answer("✅ Спасибо за ваше обращение!\n"
                             "Ваша заявка успешно отправлена. Мы свяжемся с вами в ближайшее время.")
        await state.clear()


@router.callback_query(F.data == 'cancel_cooperation')
async def cancel_cooperation_request(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Заявка на сотрудничество была отменена.")
    await callback.answer()
