from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from bot.buttons.buttons import Buttons
from bot.database.db import Database
from bot.message_texts.constans import TEACHER_START_TEXT, START_TEXT, STUDENT_START_TEXT
from bot.misc.states import MainStates


class Start:
    def __init__(self, bot : Bot, db : Database, buttons : Buttons, dp : Dispatcher):
        self.bot = bot
        self.db = db
        self.buttons = buttons
        dp.register_message_handler(self.start_message, commands=['start'], state="*")

    async def start_message(self, message : Message,state : FSMContext):
        if self.db.is_teacher(message.chat.id,message.from_user.username):
            await message.answer(text=TEACHER_START_TEXT.format(self.db.get_teacher_name_by_chat_id(message.chat.id)),
                                 reply_markup=self.buttons.get_flow_for_teacher(self.db.get_teacher_id_by_chat_id(message.chat.id)))
            await state.update_data(flow_id = None)
            await MainStates.teacher.set()
        elif self.db.is_student(message.chat.id, message.from_user.username):
            await message.answer(text=STUDENT_START_TEXT.format(self.db.get_student_name_by_chat_id(message.chat.id)),
                                 reply_markup=self.buttons.get_flow_for_student(
                                     self.db.get_student_id_by_chat_id(message.chat.id)))
        else:
            await self.bot.send_photo(chat_id=message.chat.id,
                             photo=open('bot/image/rafail.png', 'rb'),
                             caption=START_TEXT.format(message.from_user.first_name),
                             reply_markup=self.buttons.get_courses_buttons())
            await state.update_data(course_id = None)
            await MainStates.registration.set()