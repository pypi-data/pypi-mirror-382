from aiogram import Router

from . import create_ticket, support

dialog_router = Router()

dialog_router.include_routers(
    support.dialog,
    create_ticket.dialog,
)
