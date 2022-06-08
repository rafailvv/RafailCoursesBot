from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.buttons.buttons import Buttons
from bot.database.db import Database
from bot.message_texts.constans import SELECTED_FLOW_TEACHER_TEXT, CONNECT_TO_LINK, FLOW_LIST_TEXT, \
    NOTIFICATION_STUDENT_START_LESSON_TEXT, STUDENT_INFO_TEXT
from bot.misc.states import MainStates


class Teacher:
    def __init__(self, bot: Bot, db: Database, buttons: Buttons, dp: Dispatcher):
        self.bot = bot
        self.db = db
        self.buttons = buttons
        dp.register_message_handler(self.text_handler, state=MainStates.teacher)
        dp.register_callback_query_handler(self.student_info, state=MainStates.teacher)


    async def student_info(self,callback : CallbackQuery):
        chat_id = callback.data
        fio, username, phone = self.db.get_student_info(chat_id)
        await callback.message.answer(text=STUDENT_INFO_TEXT.format(fio, username, phone))

    async def text_handler(self, message : Message, state : FSMContext):
        state_data = await state.get_data()
        if state_data['flow_id'] is None:
            course_name, dates = message.text.split(" | ")[0], message.text.split(" | ")[1]
            start_date, finish_date = dates.split(" - ")[0], dates.split(" - ")[1]
            await state.update_data(flow_id = self.db.get_flow_id_by_course_and_date(course_name, start_date, finish_date, message.from_user.id))
            await message.answer(text=SELECTED_FLOW_TEACHER_TEXT. format(message.text[2:]),
                                 reply_markup=self.buttons.in_flow())
        elif message.text == self.buttons.lesson_link_btn.text:
            await message.answer(text=CONNECT_TO_LINK,
                                 reply_markup=self.buttons.get_link_to_lesson(state_data['flow_id']))
            for student_chat_id in self.db.get_chat_id_students_in_flow(state_data['flow_id']):
                await self.bot.send_message(chat_id=student_chat_id[0],
                                            text=NOTIFICATION_STUDENT_START_LESSON_TEXT,
                                            reply_markup=self.buttons.get_link_to_lesson(state_data['flow_id']))
        elif message.text == self.buttons.back_to_flow_btn.text:
            await state.update_data(flow_id = None)
            await message.answer(text=FLOW_LIST_TEXT,
                                 reply_markup=self.buttons.get_flow_for_teacher(self.db.get_teacher_id_by_chat_id(message.chat.id)))

        elif message.text == self.buttons.student_list_btn.text:
            await message.answer(text="Список учащихся 👇🏼", reply_markup=self.buttons.get_students_names_in_flow(state_data['flow_id']))
        elif message.text == self.buttons.lesson_video_btn.text:
            pass
        else:
            await message.answer("К сожалению, я вас не понимаю 😢")
