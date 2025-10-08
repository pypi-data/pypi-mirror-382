from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Next, SwitchTo
from aiogram_dialog.widgets.text import Const

from .. import states

window = Window(
    Const('Введите текст тикета:'),
    TextInput(
        'text',
        on_success=Next(),
    ),
    SwitchTo(
        text=Const('Назад'),
        id='back',
        state=states.CreateTicket.ENTER_TITLE,
    ),
    state=states.CreateTicket.ENTER_TEXT,
)
