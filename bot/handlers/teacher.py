import locale
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType, InputMediaVideo

from bot.buttons.buttons import Buttons
from bot.database.db import Database
from bot.message_texts.constans import SELECTED_FLOW_TEXT, CONNECT_TO_LINK_TEACHER, FLOW_LIST_TEXT, \
    NOTIFICATION_STUDENT_START_LESSON_TEXT, PERSON_INFO_TEXT, LESSON_RECORDING_FOR_STUDENT_TEXT
from bot.misc.states import MainStates, Recording


class Teacher:
    def __init__(self, bot: Bot, db: Database, buttons: Buttons, dp: Dispatcher):
        self.bot = bot
        self.db = db
        self.buttons = buttons
        dp.register_message_handler(self.text_handler, state=MainStates.teacher)
        # dp.register_callback_query_handler(self.inline_keyboard_handler,
        #                                    state=[MainStates.teacher, Recording.edit_video, Recording.edit_description])
        dp.register_message_handler(self.send_recordings,
                                    state=[MainStates.teacher, Recording.video, Recording.description],
                                    content_types=ContentType.ANY)
        dp.register_message_handler(self.edit_send_recordings,
                                    state=[MainStates.teacher, Recording.edit_video, Recording.edit_description],
                                    content_types=ContentType.ANY)

    async def send_recordings(self, message: Message, state: FSMContext):
        if message.text in [self.buttons.lesson_link_btn.text, self.buttons.lesson_video_btn.text,
                            self.buttons.student_list_btn.text, self.buttons.check_homework_btn.text,
                            self.buttons.back_to_courses_btn.text]:
            await self.text_handler(message, state)
            await MainStates.teacher.set()
        else:
            cur_state = await state.get_state()
            if cur_state == Recording.video.state:
                await state.update_data(video_id=message.video.file_id)
                await message.answer(text="📝 Опишите кратно темы, которые были изучены на этом занятии")
                await Recording.description.set()
            elif cur_state == Recording.description.state:
                await state.update_data(description="📝 На данном занятии были пройдены такие темы, как " +
                                                    message.text[0].lower() + message.text[1:])
                data = await state.get_data()
                lesson_recording = await self.bot.send_video(chat_id=message.chat.id,
                                                             video=data['video_id'],
                                                             caption=data['description'],
                                                             reply_markup=self.buttons.edit_recording_info())
                await state.update_data(lesson_recording_message_id=lesson_recording.message_id)
                await MainStates.teacher.set()

    async def edit_send_recordings(self, message: Message, state: FSMContext):
        if message.text in [self.buttons.lesson_link_btn.text, self.buttons.lesson_video_btn.text,
                            self.buttons.student_list_btn.text, self.buttons.check_homework_btn.text,
                            self.buttons.back_to_courses_btn.text]:
            await self.text_handler(message, state)
            await MainStates.teacher.set()
        else:
            cur_state = await state.get_state()
            if cur_state == Recording.edit_video.state:
                await state.update_data(video_id=message.video.file_id)
                data = await state.get_data()
                await self.bot.edit_message_media(media=InputMediaVideo(message.video.file_id),
                                                  chat_id=message.chat.id,
                                                  message_id=data['lesson_recording_message_id'],
                                                  reply_markup=self.buttons.edit_recording_info())
                await message.answer(
                    "Данные успешно изменены!\n\nНажмите кнопку <b>Подтвердить</b> выше, если данные корректны 👆")
                await MainStates.teacher.set()
            elif cur_state == Recording.edit_description.state:
                await state.update_data(description="📝 На данном занятии были пройдены такие темы, как " +
                                                    message.text[0].lower() + message.text[1:])
                data = await state.get_data()
                await self.bot.edit_message_caption(caption=data['description'],
                                                    chat_id=message.chat.id,
                                                    message_id=data['lesson_recording_message_id'],
                                                    reply_markup=self.buttons.edit_recording_info())
                await message.answer(
                    "Данные успешно изменены!\n\nНажмите кнопку <b>Подтвердить</b> выше, если данные корректны 👆")
                await MainStates.teacher.set()

    # async def inline_keyboard_handler(self, callback: CallbackQuery, state: FSMContext):
    #     data = callback.data.split("|")
        # if data[0] == "Record":
        #     if data[1] == "video":
        #         await callback.message.answer(text="📨 Пришлите видеозапись последнего занятия")
        #         await Recording.edit_video.set()
        #     elif data[1] == "description":
        #         await callback.message.answer(text="📝 Опишите кратно темы, которые были пройдены на этом занятии")
        #         await Recording.edit_description.set()
        #     elif data[1] == "accept":
        #         data_state = await state.get_data()
        #         await self.bot.delete_message(chat_id=callback.message.chat.id,
        #                                       message_id=data_state['lesson_recording_message_id'])
        #         await callback.message.answer("✅ Данные подтверждены успешно!")
        #         lesson_number = self.db.save_new_recording(data_state['video_id'], data_state['description'], data_state['flow_id'])
        #
        #         locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
        #         for student_chat_id in self.db.get_students_chat_id_in_flow(data_state['flow_id']):
        #             await self.bot.send_video(chat_id= student_chat_id,
        #                                       video=data_state['video_id'],
        #                                       caption=LESSON_RECORDING_FOR_STUDENT_TEXT.format(
        #                                           datetime.now().strftime("%d %B"),
        #                                           self.db.get_students_chat_id_in_flow(data_state['flow_id']),
        #                                           lesson_number, data_state['description']))
        # if data[0] == "Student":
        #     chat_id = data[1]
        #     fio, username, phone = self.db.get_student_info(chat_id)
        #     await callback.message.answer(text=PERSON_INFO_TEXT.format("👨‍🎓", fio, username, phone))

    async def text_handler(self, message: Message, state: FSMContext):
        state_data = await state.get_data()
        if state_data['flow_id'] is None:
            course_name, dates = message.text.split(" | ")[0], message.text.split(" | ")[1]
            start_date, finish_date = dates.split(" - ")[0], dates.split(" - ")[1]
            await state.update_data(flow_id=self.db.get_flow_id_by_course_and_date(course_name, start_date, finish_date,
                                                                                   message.from_user.id))
            await message.answer(text=SELECTED_FLOW_TEXT.format(message.text[2:]),
                                 reply_markup=self.buttons.in_flow_teacher())
        elif message.text == self.buttons.lesson_link_btn.text:
            await message.answer(text=CONNECT_TO_LINK_TEACHER,
                                 reply_markup=self.buttons.get_link_to_lesson(state_data['flow_id']))
            for student_chat_id in self.db.get_chat_id_students_in_flow(state_data['flow_id']):
                await self.bot.send_message(chat_id=student_chat_id[0],
                                            text=NOTIFICATION_STUDENT_START_LESSON_TEXT,
                                            reply_markup=self.buttons.get_link_to_lesson(state_data['flow_id']))
        elif message.text == self.buttons.back_to_flow_btn.text:
            await state.update_data(flow_id=None)
            await message.answer(text=FLOW_LIST_TEXT,
                                 reply_markup=self.buttons.get_flow_for_teacher(
                                     self.db.get_teacher_id_by_chat_id(message.chat.id)))

        elif message.text == self.buttons.student_list_btn.text:
            await message.answer(text="Список учащихся 👇🏼",
                                 reply_markup=self.buttons.get_students_names_in_flow(state_data['flow_id']))
        elif message.text == self.buttons.lesson_video_btn.text:
            await message.answer(text="📨 Пришлите видеозапись последнего занятия")
            await Recording.video.set()
        elif message.text == self.buttons.check_homework_btn.text:
            # TODO
            pass
        else:
            await message.answer("К сожалению, я Вас не понимаю 😢")
