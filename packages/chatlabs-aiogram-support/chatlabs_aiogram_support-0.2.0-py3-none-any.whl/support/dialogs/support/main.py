from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Cancel, Start, SwitchTo
from aiogram_dialog.widgets.text import Const

from .. import states

window = Window(
    Const('Поддержка'),
    SwitchTo(
        text=Const('Открытые тикеты'),
        id='swith_to_open_tickets',
        state=states.Support.OPEN_TICKETS,
    ),
    SwitchTo(
        text=Const('Закрытые тикеты'),
        id='swith_to_close_tickets',
        state=states.Support.CLOSE_TICKETS,
    ),
    Start(
        text=Const('Создать тикет'),
        id='start_create_ticket',
        state=states.CreateTicket.ENTER_TITLE,
    ),
    Cancel(Const('Назад')),
    state=states.Support.MAIN,
)
