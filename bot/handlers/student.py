from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ContentType

from bot.buttons.buttons import Buttons
from bot.database.db import Database
from bot.message_texts.constans import STUDENT_START_TEXT, SELECTED_FLOW_TEXT, FLOW_LIST_TEXT, TIMETABLE_TEXT, \
    COURSES_LIST, PERSON_INFO_TEXT, CONNECT_TO_LINK_STUDENT, FEEDBACK_TEXT
from bot.misc.states import MainStates, HomeWork


class Student:
    def __init__(self, bot: Bot, db: Database, buttons: Buttons, dp: Dispatcher):
        self.bot = bot
        self.db = db
        self.buttons = buttons
        dp.register_message_handler(self.text_handler, state = MainStates.student)
        dp.register_message_handler(
            self.completed_task,
            state = HomeWork.for_confirmation,
            content_types=ContentType.ANY)

    async def text_handler(self, message : Message, state : FSMContext):
        state_data = await state.get_data()
        if message.text == self.buttons.back_to_courses_btn.text:
            await message.answer(text=COURSES_LIST,
                                 reply_markup=self.buttons.get_courses_buttons(True))
            await state.update_data(id=None)
            await MainStates.registration.set()
        elif state_data['flow_id'] is None:
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
        elif message.text == self.buttons.teacher_info_btn.text:
            fio, username, phone = self.db.get_teacher_info(state_data['flow_id'])
            await message.answer(text=PERSON_INFO_TEXT.format("👨‍🏫", fio, username, phone))
        elif message.text == self.buttons.lesson_link_btn.text:
            await message.answer(text=CONNECT_TO_LINK_STUDENT,
                                 reply_markup=self.buttons.get_link_to_lesson(state_data['flow_id']))
        elif message.text == self.buttons.lesson_video_btn.text:
            buttons = self.buttons.get_recorded_lessons(state_data['flow_id'])
            if buttons.inline_keyboard:
                await message.answer(text="Выберите интересующее занятие 👇🏼",
                                     reply_markup=self.buttons.get_recorded_lessons(state_data['flow_id']))
            else:
                await message.answer(text="🥲 Пока нет записи ни одного занятия")
        elif message.text == self.buttons.send_homework_btn.text:
            buttons = self.buttons.get_not_done_hw(state_data['flow_id'], message.chat.id)
            if buttons.inline_keyboard:
                await message.answer(
                    text="👇 Веберите урок 👇",
                    reply_markup=buttons
                )
            else:
                await message.answer(text="🥳 Нет невыполненных домашних работ ")
        elif message.text == self.buttons.feedback_btn.text:
            await message.answer(text=FEEDBACK_TEXT)
        else:
            await message.answer("К сожалению, я тебя не понимаю 😢")

    async def completed_task(self, message : Message, state : FSMContext):
        if message.text in [self.buttons.back_to_flow_btn.text, self.buttons.lesson_link_btn.text,
                            self.buttons.teacher_info_btn.text, self.buttons.lesson_video_btn.text,
                            self.buttons.send_homework_btn.text]:
            await self.text_handler(message, state)
            await MainStates.student.set()
        else:
            is_possible = True
            await state.update_data(content_type=message.content_type)
            if message.content_type == "text":
                await message.answer(text=message.text, reply_markup=self.buttons.edit_message("HW_S"))
                await state.update_data(content=message.text)
            elif message.content_type == "document":
                await message.answer_document(document=message.document.file_id,
                                              reply_markup=self.buttons.edit_message("HW_S"))
                await state.update_data(content=message.document.file_id)
            elif message.content_type == "photo":
                await message.answer_photo(photo=message.photo[-1].file_id, caption=message.caption,
                                           reply_markup=self.buttons.edit_message("HW_S"))
                if message.caption is None:
                    await state.update_data(content=message.photo[-1].file_id)
                else:
                    await state.update_data(content=message.photo[-1].file_id + "|" + message.caption)
            elif message.content_type == "video":
                await message.answer_video(video=message.video.file_id, caption=message.caption,
                                           reply_markup=self.buttons.edit_message("HW_S"))
                if message.caption is None:
                    await state.update_data(content=message.video.file_id)
                else:
                    await state.update_data(content=message.video.file_id + "|" + message.caption)
            elif message.content_type == "voice":
                await message.answer_voice(voice=message.voice.file_id,
                                           reply_markup=self.buttons.edit_message("HW_S"))
                await state.update_data(content=message.voice.file_id)
            elif message.content_type == "video_note":
                await message.answer_video_note(video_note=message.video_note.file_id,
                                                reply_markup=self.buttons.edit_message("HW_S"))
                await state.update_data(content=message.video_note.file_id)
            else:
                is_possible = False
                await message.answer("К сожалению, данный тип сообщения не поддерживается 😢")
            if is_possible:
                hint = await message.answer("<b>Измените</b> или <b>Подтвердите</b> содержимое сообщения для отправки 👆")
                await state.update_data(hint_msg_id=hint.message_id)
                await MainStates.student.set()

