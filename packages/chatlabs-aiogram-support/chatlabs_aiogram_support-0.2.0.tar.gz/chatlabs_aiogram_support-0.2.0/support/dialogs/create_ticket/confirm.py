from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, Multi

from .. import api, states


async def confirmation_getter(dialog_manager: DialogManager, **_):
    return {
        'title': dialog_manager.find('title').get_value(),
        'text': dialog_manager.find('text').get_value(),
    }


async def confirm(
    callback: CallbackQuery,
    widget,  # noqa: ARG001
    dialog_manager: DialogManager,
):
    ticket = await api.Ticket.api_create(
        callback.from_user.id,
        dialog_manager.find('title').get_value(),
    )
    await api.Message.api_create(
        ticket.id,
        dialog_manager.find('text').get_value(),
    )
    await callback.answer('Тикет создан!')
    await dialog_manager.start(states.Support.MAIN)


window = Window(
    Multi(
        Const('Ваш тикет:'),
        Format('<b>{title}</b>'),
        Format('<i>{text}</i>'),
        sep='\n\n',
    ),
    Button(
        text=Const('Подтвердить'),
        id='confirm',
        on_click=confirm,
    ),
    SwitchTo(
        text=Const('Назад'),
        id='back',
        state=states.CreateTicket.ENTER_TEXT,
    ),
    state=states.CreateTicket.CONFIRM,
    getter=confirmation_getter,
)
