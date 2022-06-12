from aiogram.dispatcher.filters.state import State, StatesGroup


class MainStates(StatesGroup):
    registration = State()
    teacher = State()
    student = State()


class PersonalInfo(StatesGroup):
    fio = State()
    phone = State()
    username = State()

    check_info = State()

    edit_fio = State()
    edit_phone = State()
    edit_username = State()


class Recording(StatesGroup):
    description = State()
    video = State()

    edit_description = State()
    edit_video = State()


class SendAll(StatesGroup):
    send = State()


class HomeWork(StatesGroup):
    assign = State()
    for_confirmation = State()

    comment = State()
