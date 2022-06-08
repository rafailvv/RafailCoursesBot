from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from bot.buttons.buttons import Buttons
from bot.database.db import Database
from bot.message_texts.constans import STUDENT_START_TEXT, SELECTED_FLOW_TEXT, FLOW_LIST_TEXT, TIMETABLE_TEXT
from bot.misc.states import MainStates


class Student:
    def __init__(self, bot: Bot, db: Database, buttons: Buttons, dp: Dispatcher):
        self.bot = bot
        self.db = db
        self.buttons = buttons
        dp.register_message_handler(self.text_handler, state=MainStates.student)

    async def text_handler(self, message : Message, state : FSMContext):
        state_data = await state.get_data()
        if state_data['flow_id'] is None:
            course_name, dates = message.text.split(" | ")[0], message.text.split(" | ")[1]
            start_date, finish_date = dates.split(" - ")[0], dates.split(" - ")[1]
            flow_id = self.db.get_flow_id_by_course_and_date(course_name, start_date, finish_date, message.from_user.id)
            await state.update_data(flow_id=flow_id)
            await message.answer(text=TIMETABLE_TEXT.format(self.db.get_timetable_by_flow_id(flow_id)),
                                 reply_markup=self.buttons.in_flow_student())
        elif message.text == self.buttons.back_to_flow_btn.text:
            await state.update_data(flow_id=None)
            await message.answer(text=FLOW_LIST_TEXT,
                                 reply_markup=self.buttons.get_flow_for_student(
                                     self.db.get_student_id_by_chat_id(message.chat.id)))
