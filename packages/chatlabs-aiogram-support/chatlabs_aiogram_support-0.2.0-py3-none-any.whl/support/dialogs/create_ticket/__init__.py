from aiogram_dialog import Dialog

from . import confirm, enter_text, enter_title

dialog = Dialog(
    enter_title.window,
    enter_text.window,
    confirm.window,
)
