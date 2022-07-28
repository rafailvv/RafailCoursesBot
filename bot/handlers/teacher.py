from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ContentType, InputMediaVideo

from bot.buttons.buttons import Buttons
from bot.database.db import Database
from bot.message_texts.constans import get_text_by_key
from bot.misc.states import MainStates, Recording, SendAll, HomeWork


class Teacher:
    def __init__(self, bot: Bot, db: Database, buttons: Buttons, dp: Dispatcher):
        self.bot = bot
        self.db = db
        self.buttons = buttons
        dp.register_message_handler(self.text_handler, state=MainStates.teacher)
        dp.register_message_handler(self.send_recordings,
                                    state=[MainStates.teacher, Recording.video, Recording.description],
                                    content_types=ContentType.ANY)
        dp.register_message_handler(self.edit_send_recordings,
                                    state=[MainStates.teacher, Recording.edit_video, Recording.edit_description],
                                    content_types=ContentType.ANY)
        dp.register_message_handler(self.send_all_student,
                                    state=SendAll.send,
                                    content_types=ContentType.ANY)
        dp.register_message_handler(self.assign_homework,
                                    state = HomeWork.assign,
                                    content_types=ContentType.ANY)
        dp.register_message_handler(self.take_comment,
                                    state=HomeWork.comment,
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
                if message.content_type == "video":
                    await state.update_data(video_id=message.video.file_id)
                    await message.answer(text="📝 Кратко опишите темы, которые были изучены на этом занятии")
                    await Recording.description.set()
                else:
                    await message.answer("❗Отправьте видеозапись занятия в <b>формате видео</b>❗")
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

    async def text_handler(self, message: Message, state: FSMContext):
        state_data = await state.get_data()
        if state_data['flow_id'] is None:
            course_name, dates = message.text.split(" | ")[0], message.text.split(" | ")[1]
            start_date, finish_date = dates.split(" - ")[0], dates.split(" - ")[1]
            await state.update_data(flow_id=self.db.get_flow_id_by_course_and_date(course_name, start_date, finish_date,
                                                                                   message.from_user.id))
            await message.answer(text=get_text_by_key('SELECTED_FLOW_TEXT').format(message.text[2:]),
                                 reply_markup=self.buttons.in_flow_teacher())
        elif message.text == self.buttons.lesson_link_btn.text:
            await message.answer(text=get_text_by_key('CONNECT_TO_LINK_TEACHER'),
                                 reply_markup=self.buttons.get_link_to_lesson(state_data['flow_id']))
            for student_chat_id in self.db.get_chat_id_students_in_flow(state_data['flow_id']):
                await self.bot.send_message(chat_id=student_chat_id[0],
                                            text=get_text_by_key('NOTIFICATION_STUDENT_START_LESSON_TEXT'),
                                            reply_markup=self.buttons.get_link_to_lesson(state_data['flow_id']))
        elif message.text == self.buttons.back_to_flow_btn.text:
            await state.update_data(flow_id=None)
            await message.answer(text=get_text_by_key('FLOW_LIST_TEXT'),
                                 reply_markup=self.buttons.get_flow_for_teacher(
                                     self.db.get_teacher_id_by_chat_id(message.chat.id)))

        elif message.text == self.buttons.student_list_btn.text:
            await message.answer(text="👇 Список учащихся 👇",
                                 reply_markup=self.buttons.get_students_list_in_flow(state_data['flow_id']))
        elif message.text == self.buttons.lesson_video_btn.text:
            await message.answer(text="📨 Пришлите видеозапись последнего занятия")
            await Recording.video.set()
        elif message.text == self.buttons.check_homework_btn.text:
            await message.answer(text="👇 Выберите действие 👇",
                                 reply_markup=self.buttons.home_action_selection())
        else:
            await message.answer("К сожалению, я Вас не понимаю 😢")

    async def send_all_student(self, message: Message, state: FSMContext):
        if message.text in [self.buttons.lesson_link_btn.text, self.buttons.lesson_video_btn.text,
                            self.buttons.student_list_btn.text, self.buttons.check_homework_btn.text,
                            self.buttons.back_to_courses_btn.text]:
            await self.text_handler(message, state)
            await MainStates.teacher.set()
        else:
            is_possible = True
            if message.content_type == "text.txt":
                await message.answer(text=message.text, reply_markup=self.buttons.edit_message("SendAll"))
            elif message.content_type == "document":
                await message.answer_document(document=message.document.file_id,
                                              reply_markup=self.buttons.edit_message("SendAll"))
            elif message.content_type == "photo":
                await message.answer_photo(photo=message.photo[-1].file_id, caption=message.caption,
                                           reply_markup=self.buttons.edit_message("SendAll"))
            elif message.content_type == "video":
                await message.answer_video(video=message.video.file_id, caption=message.caption,
                                           reply_markup=self.buttons.edit_message("SendAll"))
            elif message.content_type == "voice":
                await message.answer_voice(voice=message.voice.file_id,
                                           reply_markup=self.buttons.edit_message("SendAll"))
            elif message.content_type == "video_note":
                await message.answer_video_note(video_note=message.video_note.file_id,
                                                reply_markup=self.buttons.edit_message("SendAll"))
            else:
                is_possible = False
                await message.answer("К сожалению, данный тип сообщения не поддерживается 😢")
            if is_possible:
                hint = await message.answer("<b>Измените</b> или <b>Подтвердите</b> содержимое сообщения для отправки 👆")
                await state.update_data(hint_msg_id=hint.message_id)
                await MainStates.teacher.set()

    async def assign_homework(self, message : Message, state : FSMContext):
        if message.text in [self.buttons.lesson_link_btn.text, self.buttons.lesson_video_btn.text,
                            self.buttons.student_list_btn.text, self.buttons.check_homework_btn.text,
                            self.buttons.back_to_courses_btn.text]:
            await self.text_handler(message, state)
            await MainStates.teacher.set()
        else:
            is_possible = True
            await state.update_data(content_type=message.content_type)
            if message.content_type == "text.txt":
                await message.answer(text=message.text, reply_markup=self.buttons.edit_message("HW_T"))
                await state.update_data(content =message.text )
            elif message.content_type == "document":
                await message.answer_document(document=message.document.file_id,
                                              reply_markup=self.buttons.edit_message("HW_T"))
                await state.update_data(content=message.document.file_id)
            elif message.content_type == "photo":
                await message.answer_photo(photo=message.photo[-1].file_id, caption=message.caption,
                                           reply_markup=self.buttons.edit_message("HW_T"))
                if message.caption is None:
                    await state.update_data(content=message.photo[-1].file_id)
                else:
                    await state.update_data(content=message.photo[-1].file_id + "|" + message.caption)
            elif message.content_type == "video":
                await message.answer_video(video=message.video.file_id, caption=message.caption,
                                           reply_markup=self.buttons.edit_message("HW_T"))
                if message.caption is None:
                    await state.update_data(content=message.video.file_id )
                else:
                    await state.update_data(content=message.video.file_id + "|" + message.caption)
            elif message.content_type == "voice":
                await message.answer_voice(voice=message.voice.file_id,
                                           reply_markup=self.buttons.edit_message("HW_T"))
                await state.update_data(content=message.voice.file_id)
            elif message.content_type == "video_note":
                await message.answer_video_note(video_note=message.video_note.file_id,
                                                reply_markup=self.buttons.edit_message("HW_T"))
                await state.update_data(content=message.video_note.file_id)
            else:
                is_possible = False
                await message.answer("К сожалению, данный тип сообщения не поддерживается 😢")
            if is_possible:
                hint = await message.answer("<b>Измените</b> или <b>Подтвердите</b> содержимое сообщения для отправки 👆")
                await state.update_data(hint_msg_id = hint.message_id)
                await MainStates.teacher.set()

    async def take_comment(self, message : Message, state : FSMContext):
        # TODO any types
        data = await state.get_data()
        hw_id = data['hw_id']

        await self.bot.send_message(
            chat_id=self.db.get_student_chat_id_by_hw_id(hw_id),
            text=get_text_by_key('REJECTED_HW_TEXT').format(
                self.db.get_teacher_fio_by_hw_id(hw_id),
                self.db.get_lesson_number_by_hw_id(hw_id),
                message.text[0].lower() + message.text[1:]
            )
        )

        await message.answer(text="✅ Комментарий успешно отправлен")
        await MainStates.teacher.set()