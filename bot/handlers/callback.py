from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from bot.buttons.buttons import Buttons
from bot.database.db import Database
from bot.message_texts.constans import REJECTED_TEXT, ACCEPTED_TEXT, BUY_COURSE_TEXT, INFO_FOR_BUY_COURSE, ID_RAFAIL, \
    PERSON_INFO_TEXT, LESSON_RECORDING_FOR_STUDENT_TEXT, NEW_HW_TEXT, NEW_MSG_TEXT, SOLUTION_HW_TEXT, ACCEPTED_HW_TEXT
from bot.misc.states import PersonalInfo, MainStates, Recording, SendAll, HomeWork


class Callback:
    def __init__(self, bot: Bot, db: Database, buttons: Buttons, dp: Dispatcher):
        self.bot = bot
        self.db = db
        self.buttons = buttons
        dp.register_callback_query_handler(self.callback_handler, state="*")

    async def callback_handler(self, callback: CallbackQuery, state: FSMContext):
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

                await self.bot.send_message(
                    chat_id=ID_RAFAIL,
                    text=INFO_FOR_BUY_COURSE.format(
                        callback.message.chat.username,
                        self.db.get_course_name_by_course_id(state_data['course_id'])[2:],
                        state_data['fio'],
                        state_data['phone'],
                        state_data['username']
                    ),
                    reply_markup=self.buttons.get_confirm_and_reject(
                        callback.message.chat.id, state_data['course_id'],
                        self.db.get_student_id_by_username(state_data['username'])))
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
                lesson_number = self.db.save_new_recording(data_state['video_id'], data_state['description'],
                                                           data_state['flow_id'])

                for student_chat_id in self.db.get_students_chat_id_in_flow(data_state['flow_id']):
                    await self.bot.send_video(chat_id=student_chat_id[0],
                                              video=data_state['video_id'],
                                              caption=LESSON_RECORDING_FOR_STUDENT_TEXT.format(
                                                  datetime.now().strftime("%d.%m"),
                                                  self.db.get_course_name_by_course_id(data_state['flow_id'])[2:],
                                                  lesson_number, data_state['description']))
        elif data[0] == "Student":
            student_id = data[1]
            fio, username, phone = self.db.get_student_info(student_id)
            await callback.message.answer(text=PERSON_INFO_TEXT.format("👨‍🎓", fio, username, phone))

        elif data[0] == "SendAll":

            await self.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
            )

            if data[1] == "send":
                await self.bot.send_message(chat_id=callback.message.chat.id,
                                            text="🙏 Пришлите содержимое сообщения")
                await SendAll.send.set()
            elif data[1] == "edit":
                await self.bot.send_message(chat_id=callback.message.chat.id,
                                            text="🙏 Пришлите новое содержимое сообщения")
                await SendAll.send.set()
            elif data[1] == "accept":
                data_state = await state.get_data()

                await self.bot.delete_message(
                    chat_id=callback.message.chat.id,
                    message_id=data_state['hint_msg_id']
                )

                message = callback.message
                for student_chat_id in self.db.get_students_chat_id_in_flow(data_state['flow_id']):
                    student_chat_id = student_chat_id[0]
                    await self.bot.send_message(
                        chat_id=student_chat_id,
                        text=NEW_MSG_TEXT.format(self.db.get_fio_teacher_by_chat_id(callback.message.chat.id)))
                    if message.content_type == "text":
                        await self.bot.send_message(
                            chat_id=student_chat_id,
                            text=message.text)
                    elif message.content_type == "document":
                        await self.bot.send_document(
                            chat_id=student_chat_id,
                            document=message.document.file_id)
                    elif message.content_type == "photo":
                        await self.bot.send_photo(
                            chat_id=student_chat_id,
                            photo=message.photo[-1].file_id,
                            caption=message.caption)
                    elif message.content_type == "video":
                        await self.bot.send_video(
                            chat_id=student_chat_id,
                            video=message.video.file_id,
                            caption=message.caption)
                    elif message.content_type == "voice":
                        await self.bot.send_voice(
                            chat_id=student_chat_id,
                            voice=message.voice.file_id)
                    elif message.content_type == "video_note":
                        await self.bot.send_video_note(
                            chat_id=student_chat_id,
                            video_note=message.video_note.file_id)

                await self.bot.send_message(chat_id=message.chat.id, text="👍 Сообщение успешно отправлено!")

        elif data[0] == "RecLesson":
            lesson_date, course_name, lesson_number, description, recording = self.db.get_recorded_lesson(int(data[1]))
            lesson_date = f"{lesson_date.split('-')[2]}.{lesson_date.split('-')[1]}"
            await self.bot.send_video(
                chat_id=callback.message.chat.id,
                video=recording,
                caption=LESSON_RECORDING_FOR_STUDENT_TEXT.format(lesson_date, course_name[2:],
                                                                 lesson_number, description))

        elif data[0] == "HW_T":
            if data[1] == "assign":
                buttons = self.buttons.get_past_lessons(state_data['flow_id'])
                await self.bot.delete_message(
                    chat_id=callback.message.chat.id,
                    message_id=callback.message.message_id,
                )


                if buttons.inline_keyboard:
                    await self.bot.send_message(
                        chat_id=callback.message.chat.id,
                        text="👇 Веберите урок 👇",
                        reply_markup=self.buttons.get_past_lessons(state_data['flow_id'])
                    )
                else:
                    await self.bot.send_message(
                        chat_id=callback.message.chat.id,
                        text="🥲 Ни один урок не был загружен", )

            elif data[1] == "check":
                await self.bot.delete_message(
                    chat_id=callback.message.chat.id,
                    message_id=callback.message.message_id,
                )
                buttons = self.buttons.get_unchecked_lessons(state_data['flow_id'])
                if buttons.inline_keyboard:
                    await self.bot.send_message(
                        chat_id=callback.message.chat.id,
                        text="👇 Веберите урок 👇",
                        reply_markup=self.buttons.get_unchecked_lessons(state_data['flow_id'])
                    )
                else:
                    await self.bot.send_message(
                        chat_id=callback.message.chat.id,
                        text="🥳 Непроверенных домашних заданий нет",
                        reply_markup=self.buttons.get_unchecked_lessons(state_data['flow_id'])
                    )
            elif data[1] == "checkles":
                await self.bot.delete_message(
                    chat_id=callback.message.chat.id,
                    message_id=callback.message.message_id,
                )
                lesson_number = data[2]
                await self.bot.send_message(
                    chat_id=callback.message.chat.id,
                    text="👇 Веберите учащегося 👇",
                    reply_markup=self.buttons.get_names_unchecked_lessons(state_data['flow_id'],lesson_number)
                )
            elif 'num_les' in data[1]:
                await self.bot.delete_message(
                    chat_id=callback.message.chat.id,
                    message_id=callback.message.message_id,
                )
                await self.bot.send_message(
                    chat_id=callback.message.chat.id,
                    text="🎓 Опишите условие домашней работы",
                )
                await state.update_data(num_les=data[1].split()[1])
                await HomeWork.assign.set()

            elif data[1] == "edit":
                await self.bot.send_message(chat_id=callback.message.chat.id,
                                            text="🎓 Опишите новое условие домашней работы")
                await HomeWork.assign.set()

            elif data[1] == "accept":
                state_data = await state.get_data()

                await self.bot.delete_message(
                    chat_id=callback.message.chat.id,
                    message_id=callback.message.message_id,
                )


                await self.bot.delete_message(
                    chat_id=callback.message.chat.id,
                    message_id=state_data['hint_msg_id']
                )

                for student_chat_id in self.db.get_students_chat_id_in_flow(state_data['flow_id']):
                    hw_id = self.db.add_hw(
                        flow_id=state_data['flow_id'],
                        lesson_number=state_data['num_les'],
                        student_id=self.db.get_student_id_by_chat_id(student_chat_id[0]),
                        content=state_data['content'],
                        content_type=state_data['content_type']
                    )
                    await self.bot.send_message(
                        chat_id=student_chat_id[0],
                        text=NEW_HW_TEXT.format(
                            self.db.get_fio_teacher_by_chat_id(callback.message.chat.id),
                            state_data['num_les']
                        ),
                        reply_markup=self.buttons.get_show_hw(hw_id))

                await self.bot.send_message(
                    chat_id=callback.message.chat.id,
                    text="👍 Домашнее задание успешно назначено!"
                )

            elif data[1] == "solution":
                await self.bot.delete_message(
                    chat_id=callback.message.chat.id,
                    message_id=callback.message.message_id,
                )

                await state.update_data(hw_id=int(data[2]))

                content, content_type = self.db.get_hw_solution(int(data[2]))
                content = content.split("|")
                if len(content) == 2:
                    caption = content[1]
                    content = content[0]
                else:
                    content = content[0]
                    caption = ""
                message = callback.message
                if content_type == "text":
                    await self.bot.send_message(
                        chat_id=message.chat.id,
                        text=content,
                        reply_markup=self.buttons.get_confirmation(int(data[2])))
                elif content_type == "document":
                    await self.bot.send_document(
                        chat_id=message.chat.id,
                        document=content,
                        reply_markup=self.buttons.get_confirmation(int(data[2])))
                elif content_type == "photo":
                    await self.bot.send_photo(
                        chat_id=message.chat.id,
                        photo=content,
                        caption=caption,
                        reply_markup=self.buttons.get_confirmation(int(data[2])))
                elif content_type == "video":
                    await self.bot.send_video(
                        chat_id=message.chat.id,
                        video=content,
                        caption=caption,
                        reply_markup=self.buttons.get_confirmation(int(data[2])))
                elif content_type == "voice":
                    await self.bot.send_voice(
                        chat_id=message.chat.id,
                        voice=content,
                        reply_markup=self.buttons.get_confirmation(int(data[2])))
                elif content_type == "video_note":
                    await self.bot.send_video_note(
                        chat_id=message.chat.id,
                        video_note=content,
                        reply_markup=self.buttons.get_student_send_hw(int(data[2])))
            elif data[1] == "conf":
                hw_id = data[3]
                if data[2] == "acp":
                    await self.bot.delete_message(
                        chat_id=callback.message.chat.id,
                        message_id=callback.message.message_id,
                    )

                    self.db.accept_homework(hw_id)

                    await self.bot.send_message(
                        chat_id=self.db.get_student_chat_id_by_hw_id(hw_id),
                        text=ACCEPTED_HW_TEXT.format(
                            self.db.get_teacher_fio_by_hw_id(hw_id),
                            self.db.get_lesson_number_by_hw_id(hw_id)
                        )
                    )
                else:
                    await self.bot.delete_message(
                        chat_id=callback.message.chat.id,
                        message_id=callback.message.message_id,
                    )

                    self.db.reject_homework(hw_id)

                    await self.bot.send_message(
                        chat_id=callback.message.chat.id,
                        text="🤓 Отавьте комментарий ученику"
                    )

                    await HomeWork.comment.set()
                    await state.update_data(hw_id = hw_id)
                    # await self.bot.send_message(
                    #     chat_id=self.db.get_student_chat_id_by_hw_id(hw_id),
                    #     text=REJECTED_HW_TEXT.format(
                    #         self.db.get_teacher_fio_by_hw_id(hw_id),
                    #         self.db.get_lesson_number_by_hw_id(hw_id)
                    #     )
                    # )




        elif data[0] == "HW_S":
            if data[1] == "show":
                await self.bot.delete_message(
                    chat_id=callback.message.chat.id,
                    message_id=callback.message.message_id,
                )

                content, content_type = self.db.get_hw(int(data[2]))
                content = content.split("|")
                if len(content) == 2:
                    caption = content[1]
                    content = content[0]
                else:
                    content = content[0]
                    caption = ""
                message = callback.message
                if content_type == "text":
                    await self.bot.send_message(
                        chat_id=message.chat.id,
                        text=content,
                        reply_markup=self.buttons.get_student_send_hw(int(data[2])))
                elif content_type == "document":
                    await self.bot.send_document(
                        chat_id=message.chat.id,
                        document=content,
                        reply_markup=self.buttons.get_student_send_hw(int(data[2])))
                elif content_type == "photo":
                    await self.bot.send_photo(
                        chat_id=message.chat.id,
                        photo=content,
                        caption=caption,
                        reply_markup=self.buttons.get_student_send_hw(int(data[2])))
                elif content_type == "video":
                    await self.bot.send_video(
                        chat_id=message.chat.id,
                        video=content,
                        caption=caption,
                        reply_markup=self.buttons.get_student_send_hw(int(data[2])))
                elif content_type == "voice":
                    await self.bot.send_voice(
                        chat_id=message.chat.id,
                        voice=content,
                        reply_markup=self.buttons.get_student_send_hw(int(data[2])))
                elif content_type == "video_note":
                    await self.bot.send_video_note(
                        chat_id=message.chat.id,
                        video_note=content,
                        reply_markup=self.buttons.get_student_send_hw(int(data[2])))

            elif data[1] == "for_confirm":
                await state.update_data(hw_id=int(data[2]))
                await self.bot.delete_message(
                    chat_id=callback.message.chat.id,
                    message_id=callback.message.message_id,
                )

                await self.bot.send_message(
                    chat_id=callback.message.chat.id,
                    text="👨‍💻 Отправь выполненное задание",
                )
                await HomeWork.for_confirmation.set()

            elif data[1] == "edit":
                await self.bot.send_message(chat_id=callback.message.chat.id,
                                            text="👨‍💻 Отправить изменённое задание")
                await HomeWork.for_confirmation.set()

            elif data[1] == "accept":
                state_data = await state.get_data()

                await self.bot.delete_message(
                    chat_id=callback.message.chat.id,
                    message_id=callback.message.message_id,
                )

                if 'hint_msg_id' in state_data.keys():
                    await self.bot.delete_message(
                        chat_id=callback.message.chat.id,
                        message_id=state_data['hint_msg_id']
                    )

                self.db.update_hw_solution(
                    id=state_data['hw_id'],
                    content=state_data['content'],
                    content_type=state_data['content_type']
                )

                await self.bot.send_message(
                    chat_id=self.db.get_teacher_chat_id_by_hw_id(state_data['hw_id']),
                    text=SOLUTION_HW_TEXT.format(
                        self.db.get_student_fio_by_hw_id(state_data['hw_id']),
                        self.db.get_lesson_number_by_hw_id(state_data['hw_id'])
                    ),
                    reply_markup=self.buttons.get_show_hw_solution(state_data['hw_id'])
                )

                await self.bot.send_message(
                    chat_id=callback.message.chat.id,
                    text="👍 Домашнее задание успешно отправлено!"
                )
