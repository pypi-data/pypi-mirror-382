from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Format

from .. import api, states


async def on_ticket_selected(
    callback: CallbackQuery,  # noqa: ARG001
    widget,  # noqa: ARG001
    dialog_manager: DialogManager,
    item_id: int,
):
    ticket = await api.Ticket.api_get(item_id)
    dialog_manager.dialog_data['ticket'] = ticket.model_dump(mode='json')
    await dialog_manager.switch_to(
        state=states.Support.TICKET_DETAILS,
    )


TicketsScrollingGroup = ScrollingGroup(
    Select(
        text=Format('{item.created_at:%d.%m.%Y} {item.title}'),
        id='tickets_select',
        item_id_getter=lambda item: item.id,
        items='tickets',
        type_factory=int,
        on_click=on_ticket_selected,
    ),
    id='tickets_scrolling_group',
    height=10,
    width=1,
    hide_on_single_page=True,
)
