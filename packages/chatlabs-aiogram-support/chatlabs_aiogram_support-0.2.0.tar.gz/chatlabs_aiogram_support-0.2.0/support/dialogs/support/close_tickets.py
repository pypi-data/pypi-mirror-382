from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from .. import states
from ..api import Ticket
from .utils import TicketsScrollingGroup


async def close_tickets_getter(dialog_manager: DialogManager, **_):
    return {
        'tickets': await Ticket.api_get_list(
            dialog_manager.event.from_user.id,
            True,
        )
    }


window = Window(
    Const('Закрытые тикеты'),
    TicketsScrollingGroup,
    SwitchTo(
        text=Const('Назад'),
        id='back',
        state=states.Support.MAIN,
    ),
    state=states.Support.CLOSE_TICKETS,
    getter=close_tickets_getter,
)
