from aiogram_dialog import Dialog

from . import close_tickets, main, open_tickets, ticket_details

dialog = Dialog(
    main.window,
    open_tickets.window,
    close_tickets.window,
    ticket_details.window,
)
