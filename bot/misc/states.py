from aiogram.dispatcher.filters.state import State, StatesGroup


class States(StatesGroup):
    registration = State()
    teacher = State()