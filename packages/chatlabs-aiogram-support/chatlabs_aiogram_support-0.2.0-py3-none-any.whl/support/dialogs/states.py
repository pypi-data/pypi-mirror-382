from aiogram.fsm.state import State, StatesGroup


class Support(StatesGroup):
    MAIN = State()
    OPEN_TICKETS = State()
    CLOSE_TICKETS = State()
    TICKET_DETAILS = State()


class CreateTicket(StatesGroup):
    ENTER_TITLE = State()
    ENTER_TEXT = State()
    CONFIRM = State()
