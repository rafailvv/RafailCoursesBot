from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from bot.buttons.buttons import Buttons
from bot.database.db import Database
from bot.message_texts.constans import TEACHER_START_TEXT, START_TEXT, STUDENT_START_TEXT, NEW_UPDATE_TEXT, HELP
from bot.misc.states import MainStates


class Start:
    def __init__(self, bot : Bot, db : Database, buttons : Buttons, dp : Dispatcher):
        self.bot = bot
        self.db = db
        self.buttons = buttons


        dp.register_message_handler(self.start_message, commands=['start'], state="*")
        dp.register_message_handler(self.help_message, commands=['help'], state="*")

    async def send_upsated_bot_message(self):
        chat_ids = self.db.get_chat_id_all_users()
        if chat_ids is not None:
            for user_chat_id in chat_ids :
                user_chat_id = user_chat_id[0]
                try:
                     await self.bot.send_message(
                        chat_id=user_chat_id,
                        text=NEW_UPDATE_TEXT
                    )
                except Exception:
                    self.db.delete_user(user_chat_id)

    async def start_message(self, message : Message,state : FSMContext):
        self.db.add_user_if_not_exits(message.chat.id, message.from_user.username)
        if self.db.is_teacher(message.chat.id,message.from_user.username):
            flows = self.buttons.get_flow_for_teacher(self.db.get_teacher_id_by_chat_id(message.chat.id))
            if flows['keyboard']:
                await message.answer(text=TEACHER_START_TEXT.format(self.db.get_teacher_name_by_chat_id(message.chat.id)),
                                     reply_markup=flows)
            else:
                await message.answer(text="🥲 На данный момент вы не являетесь преподавателем ни одного потока")
            await state.update_data(flow_id = None)
            await MainStates.teacher.set()
        elif self.db.is_student(message.chat.id, message.from_user.username):
            await message.answer(text=STUDENT_START_TEXT.format(self.db.get_student_name_by_chat_id(message.chat.id)),
                                 reply_markup=self.buttons.get_flow_for_student(
                                     self.db.get_student_id_by_chat_id(message.chat.id)))
            await state.update_data(flow_id=None)
            await MainStates.student.set()
        else:
            await self.bot.send_photo(chat_id=message.chat.id,
                             photo=open('bot/image/rafail.png', 'rb'),
                             caption=START_TEXT.format(message.from_user.first_name),
                             reply_markup=self.buttons.get_courses_buttons())
            await state.update_data(course_id = None)
            await MainStates.registration.set()

    async def help_message(self, message : Message):
        await message.answer(
            text=HELP
        )