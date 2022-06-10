from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from bot.buttons.buttons import Buttons
from bot.database.db import Database
from bot.message_texts.constans import REJECTED_TEXT, ACCEPTED_TEXT, BUY_COURSE_TEXT, INFO_FOR_BUY_COURSE, ID_RAFAIL, \
    PERSON_INFO_TEXT, LESSON_RECORDING_FOR_STUDENT_TEXT
from bot.misc.states import PersonalInfo, MainStates, Recording


class Callback:
    def __init__(self, bot : Bot, db : Database, buttons : Buttons, dp : Dispatcher):
        self.bot = bot
        self.db = db
        self.buttons = buttons
        dp.register_callback_query_handler(self.callback_handler, state="*")

    async def callback_handler(self, callback : CallbackQuery, state : FSMContext):
        data = callback.data.split("|")
        state_data = await state.get_data()
        if data[0] == "Buy":
            await self.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
            if data[1] == "Reject":
                await self.bot.send_message(chat_id=data[2],
                                            text=REJECTED_TEXT.format(
                                                self.db.get_course_name_by_course_id(data[3])[2:]))
                self.db.update_confirmation(data[4])
            if data[1] == "Accept":
                if self.db.get_student_chat_id_by_id(data[4]) is not None:
                    await self.bot.send_message(chat_id=data[2],
                                                text=ACCEPTED_TEXT.format(
                                                    self.db.get_course_name_by_course_id(data[3])[2:]),
                                                reply_markup=self.buttons.get_button_to_student_page())
                else:
                    await self.bot.send_message(chat_id=data[2],
                                                text=ACCEPTED_TEXT.format(
                                                    self.db.get_course_name_by_course_id(data[3])[2:]))
                self.db.update_confirmation(data[4], True)

        elif data[0] == "PersInfo":
            if data[1] == "fio":
                await callback.message.answer(text="🔡 Введите ФИО учащегося")
                await PersonalInfo.edit_fio.set()
            elif data[1] == "phone":
                await callback.message.answer(text="📲 Введите номер телефона учащегося")
                await PersonalInfo.edit_phone.set()
            elif data[1] == "username":
                await callback.message.answer(text="🔑 Введите ник (@....) учащегося",
                                              reply_markup=self.buttons.how_find_username())
                await PersonalInfo.edit_username.set()
            elif data[1] == "accept":
                await self.bot.delete_message(chat_id=callback.message.chat.id,
                                              message_id=state_data['corr_pi_msg'].message_id)
                await callback.message.answer("✅ Данные подтверждены успешно!")

                chat_id = None
                if state_data['username'] == callback.message.chat.username:
                    chat_id = callback.message.chat.id
                self.db.add_student(state_data['fio'], state_data['phone'], state_data['username'],
                                    self.db.get_near_course_flow_by_course_id(state_data['course_id']), chat_id)

                await callback.message.answer(
                    text=BUY_COURSE_TEXT.format(self.db.get_course_name_by_course_id(state_data['course_id'])[2:]))

                await self.bot.send_message(chat_id=ID_RAFAIL,
                                            text=INFO_FOR_BUY_COURSE.format(state_data['fio'],
                                                                            state_data['username'],
                                                                            self.db.get_course_name_by_course_id(
                                                                                state_data['course_id'])[2:]),
                                            reply_markup=self.buttons.get_confirm_and_reject(callback.message.chat.id,
                                                                                             state_data['course_id'],
                                                                                             self.db.get_student_id_by_username(
                                                                                                 state_data[
                                                                                                     'username'])))
                await MainStates.registration.set()

        elif data[0] == "Record":
            if data[1] == "video":
                await callback.message.answer(text="📨 Пришлите видеозапись последнего занятия")
                await Recording.edit_video.set()
            elif data[1] == "description":
                await callback.message.answer(text="📝 Опишите кратно темы, которые были пройдены на этом занятии")
                await Recording.edit_description.set()
            elif data[1] == "accept":
                data_state = await state.get_data()
                await self.bot.delete_message(chat_id=callback.message.chat.id,
                                              message_id=data_state['lesson_recording_message_id'])
                await callback.message.answer("✅ Данные подтверждены успешно!")
                lesson_number = self.db.save_new_recording(data_state['video_id'], data_state['description'], data_state['flow_id'])

                for student_chat_id in self.db.get_students_chat_id_in_flow(data_state['flow_id']):
                    await self.bot.send_video(chat_id= student_chat_id[0],
                                              video=data_state['video_id'],
                                              caption=LESSON_RECORDING_FOR_STUDENT_TEXT.format(
                                                  datetime.now().strftime("%d.%m"),
                                                  self.db.get_course_name_by_course_id(data_state['flow_id'])[2:],
                                                  lesson_number, data_state['description']))
        elif data[0] == "Student":
            chat_id = data[1]
            fio, username, phone = self.db.get_student_info(chat_id)
            await callback.message.answer(text=PERSON_INFO_TEXT.format("👨‍🎓", fio, username, phone))