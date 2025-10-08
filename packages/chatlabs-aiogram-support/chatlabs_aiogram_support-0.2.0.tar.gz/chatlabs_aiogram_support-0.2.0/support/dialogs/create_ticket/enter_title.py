from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Cancel, Next
from aiogram_dialog.widgets.text import Const

from .. import states

window = Window(
    Const('Введите заголовок тикета:'),
    TextInput(
        'title',
        on_success=Next(),
    ),
    Cancel(Const('Назад')),
    state=states.CreateTicket.ENTER_TITLE,
)
