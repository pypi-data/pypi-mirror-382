import aiogram.types
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import NumberedPager, SwitchTo
from aiogram_dialog.widgets.text import Case, Const, Format, List, Multi

from .. import states
from ..api import Message, Ticket


async def ticket_getter(dialog_manager: DialogManager, **_):
    ticket = Ticket.model_validate(dialog_manager.dialog_data['ticket'])
    messages = await Message.api_get_list(ticket.id)
    messages.reverse()
    return {
        'ticket': ticket,
        'messages': messages,
    }


async def on_message_input(
    message: aiogram.types.Message,  # noqa: ARG001
    widget,  # noqa: ARG001
    dialog_manager: DialogManager,
    data: str,
):
    ticket = Ticket.model_validate(dialog_manager.dialog_data['ticket'])
    await Message.api_create(ticket.id, data)


window = Window(
    Multi(
        Format('Тикет #{ticket.id} <b>{ticket.title}</b>'),
        List(
            field=Multi(
                Multi(
                    Case(
                        texts={
                            'user': Const('<b>Вы</b>'),
                            'supp': Const('<b>Менеджер</b>'),
                        },
                        selector=lambda data, *_: data['item'].sender,
                    ),
                    Format('в {item.created_at:%d.%m.%Y %H:%M}'),
                    sep=' ',
                ),
                Format('<i>{item.text}</i>'),
            ),
            items='messages',
            page_size=5,
            id='messages_list',
            sep='\n\n',
        ),
        Const(
            text='<u>Вы можете написать в чат, чтобы отправить сообщение</u>',
            when=lambda data, *_: not data['ticket'].resolved,
        ),
        sep='\n\n',
    ),
    TextInput(
        'new_message_text',
        on_success=on_message_input,
    ),
    NumberedPager(
        scroll='messages_list',
    ),
    SwitchTo(
        text=Const('Назад'),
        id='back_to_open_tickets',
        state=states.Support.OPEN_TICKETS,
        when=lambda data, *_: not data['ticket'].resolved,
    ),
    SwitchTo(
        text=Const('Назад'),
        id='back_to_close_tickets',
        state=states.Support.CLOSE_TICKETS,
        when=lambda data, *_: data['ticket'].resolved,
    ),
    state=states.Support.TICKET_DETAILS,
    getter=ticket_getter,
)
