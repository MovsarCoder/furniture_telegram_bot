from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.crud import CrudCooperation
from keyboard.keyboard_builder import make_tasks_inline_keyboard, make_row_inline_keyboards
from keyboard.button_template import get_accept_cancel_buttons, admin_kb

router = Router()


@router.callback_query(F.data == 'cooperation_requests')
async def show_requests_cooperation(callback: CallbackQuery):
    await callback.answer()
    requests = await CrudCooperation().get_all_requests()

    if requests:
        await callback.message.edit_text(
            '📋 <b>Текущие заявки на сотрудничество:</b>',
            reply_markup=make_tasks_inline_keyboard(tasks=requests, callback_data_name="task")
        )
    else:
        await callback.message.edit_text("<b>❌ Пока что нет новых заявок на сотрудничество.</b>",
                                         reply_markup=make_row_inline_keyboards(admin_kb))


@router.callback_query(F.data.startswith("task_"))
async def handle_cooperation_request(callback: CallbackQuery):
    await callback.answer()
    request_id = callback.data.removeprefix("task_")

    task = await CrudCooperation().get_requests_by_id(request_id)

    response = (
        f"<b>Заявка #{task.id}</b>\n"
        f"👤 Пользователь: @{task.username} (ID: {task.telegram_id})\n\n"
        f"📩 Сообщение от пользователя:\n{task.text_requests}\n\n"
        f"🕒 Отправлено: {task.request_created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    await callback.message.edit_text(
        response,
        reply_markup=make_row_inline_keyboards(get_accept_cancel_buttons(int(request_id)))
    )


@router.callback_query(F.data.startswith("cancel_cooperation_requests_"))
async def cancel_cooperation_request(callback: CallbackQuery):
    request_id = int(callback.data.removeprefix("cancel_cooperation_requests_"))
    await callback.answer()

    crud = CrudCooperation()
    task = await crud.get_requests_by_id(request_id)

    await crud.cancel_request(request_id)
    await callback.message.edit_text(f"❌ Заявка #{request_id} отклонена и удалена из списка.",
                                     reply_markup=make_row_inline_keyboards(admin_kb))
    await callback.answer("Заявка успешно отклонена.")

    if task:
        await callback.bot.send_message(
            chat_id=task.telegram_id,
            text='Ваш запрос на сотрудничество, к сожалению, отклонён. Мы будем рады рассмотреть ваши новые предложения!'
        )


@router.callback_query(F.data.startswith("accepted_cooperation_requests_"))
async def accept_cooperation_request(callback: CallbackQuery):
    request_id = int(callback.data.removeprefix("accepted_cooperation_requests_"))
    await callback.answer()

    crud = CrudCooperation()
    task = await crud.get_requests_by_id(request_id)

    if task:
        await crud.accept_request(request_id)
        requests_buttons = await crud.get_all_requests()
        response = (
            f"✅ Заявка #{request_id} успешно одобрена. Сотрудничество начато.\n\n"
            f"<b>Заявка #{request_id}</b>\n"
            f"👤 Пользователь: @{task.username} (ID: {task.telegram_id})\n\n"
            f"📩 Сообщение от пользователя:\n{task.text_requests}\n\n"
            f"🕒 Отправлено: {task.request_created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        await callback.bot.send_message(
            chat_id=task.telegram_id,
            text='Поздравляем! Ваш запрос на сотрудничество одобрен. В ближайшее время с вами свяжутся.'
        )

        await callback.message.edit_text(
            response,
            reply_markup=make_tasks_inline_keyboard(tasks=requests_buttons, callback_data_name="task")
        )


@router.callback_query(F.data == 'show_requests_cooperation_2')
async def show_requests_cooperation_2(callback: CallbackQuery):
    await callback.answer()
    requests = await CrudCooperation().get_all_requests()

    if requests:
        await callback.message.edit_text(
            '📋 <b>Текущие заявки на сотрудничество:</b>',
            reply_markup=make_tasks_inline_keyboard(tasks=requests, callback_data_name="task")
        )
    else:
        await callback.message.edit_text("<b>❌ Пока что нет новых заявок на сотрудничество.</b>",
                                         reply_markup=make_row_inline_keyboards(admin_kb))
