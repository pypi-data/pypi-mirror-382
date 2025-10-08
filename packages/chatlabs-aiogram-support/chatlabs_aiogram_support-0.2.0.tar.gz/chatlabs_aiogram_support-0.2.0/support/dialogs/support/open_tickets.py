from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from .. import states
from ..api import Ticket
from .utils import TicketsScrollingGroup


async def open_tickets_getter(dialog_manager: DialogManager, **_):
    return {
        'tickets': await Ticket.api_get_list(
            dialog_manager.event.from_user.id,
            False,
        )
    }


window = Window(
    Const('Открытые тикеты'),
    TicketsScrollingGroup,
    SwitchTo(
        text=Const('Назад'),
        id='back',
        state=states.Support.MAIN,
    ),
    state=states.Support.OPEN_TICKETS,
    getter=open_tickets_getter,
)
