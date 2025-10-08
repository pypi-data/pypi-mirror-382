from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from .dialogs import dialog_router, states

main_state = states.Support.MAIN

SupportStartButton = Start(
    text=Const('Поддержка'),
    id='start_support_button',
    state=main_state,
)

__all__ = [
    'SupportStartButton',
    'dialog_router',
    'main_state',
    'states',
]

__version__ = '0.2.0'
