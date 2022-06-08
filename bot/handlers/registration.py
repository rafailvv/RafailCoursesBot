from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, ContentTypes

from bot.buttons.buttons import Buttons
from bot.message_texts.constans import START_TEXT, COURSE_TEXT, COURSES_LIST, BUY_COURSE_TEXT, ID_RAFAIL, \
    INFO_FOR_BUY_COURSE, \
    REJECTED_TEXT, ACCEPTED_TEXT, SUCCESSFUL_PAYMENT_TEXT, SUCCESSFUL_PAYMENT_INFO_FOR_ADMIN, TEACHER_START_TEXT, \
    CORRECTNESS_PERSONAL_INFO, STUDENT_START_TEXT
from bot.database.db import Database
from bot.misc.states import MainStates, PersonalInfo


class Registration:
    def __init__(self, bot: Bot, db: Database, buttons: Buttons, dp: Dispatcher):
        self.bot = bot
        self.db = db
        self.buttons = buttons
        dp.register_callback_query_handler(self.registration_confirmation,
                                           state="*")
        dp.register_message_handler(self.text_handler, state=MainStates.registration)
        dp.register_message_handler(self.personal_info,
                                    state=[PersonalInfo.fio, PersonalInfo.phone, PersonalInfo.username])
        dp.register_message_handler(self.editing_personal_info,
                                    state=[PersonalInfo.edit_fio, PersonalInfo.edit_phone, PersonalInfo.edit_username])
        # dp.register_pre_checkout_query_handler(self.pre_checkout_handler, state=MainStates.registration)
        # dp.register_message_handler(self.after_payment, state=[registration], content_types=ContentTypes.SUCCESSFUL_PAYMENT)



    async def registration_confirmation(self, callback: CallbackQuery, state: FSMContext):
        data = callback.data.split("|")
        state_data = await state.get_data()
        if data[0] == "Buy":
            await self.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
            if data[1] == "Reject":
                await self.bot.send_message(chat_id=data[2],
                                            text=REJECTED_TEXT.format(self.db.get_course_name(data[3])[2:]))
                self.db.update_confirmation(data[4])
            if data[1] == "Accept":
                if self.db.get_student_chat_id_by_id(data[4]) is not None:
                    await self.bot.send_message(chat_id=data[2],
                                                text=ACCEPTED_TEXT.format(self.db.get_course_name(data[3])[2:]),
                                                reply_markup=self.buttons.get_button_to_student_page())
                else:
                    await self.bot.send_message(chat_id=data[2],
                                                text=ACCEPTED_TEXT.format(self.db.get_course_name(data[3])[2:]))
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
                await self.bot.delete_message(chat_id=callback.message.chat.id, message_id=state_data['corr_pi_msg'].message_id)
                await callback.message.answer("✅ Данные подтверждены!")

                chat_id = None
                if state_data['username'] == callback.message.chat.username:
                    chat_id = callback.message.chat.id
                self.db.add_student(state_data['fio'], state_data['phone'], state_data['username'],
                                          state_data['course_id'], chat_id)

                await callback.message.answer(
                    text=BUY_COURSE_TEXT.format(self.db.get_course_name(state_data['course_id'])[2:]))

                await self.bot.send_message(chat_id=ID_RAFAIL,
                                            text=INFO_FOR_BUY_COURSE.format(state_data['fio'],
                                                                            state_data['username'],
                                                                            self.db.get_course_name(state_data['course_id'])[2:]),
                                            reply_markup=self.buttons.get_confirm_and_reject(callback.message.chat.id,
                                                                                             state_data['course_id'],
                                                                                          self.db.get_student_id_by_username(state_data['username'])))
                await MainStates.registration.set()

    def get_ending_word_day(self, number: int):
        if 11 <= number <= 19 or number % 10 in [0, 5, 6, 7, 8, 9]:
            return "дней"
        elif number % 10 == 1:
            return "день"
        elif 2 <= number % 10 <= 4:
            return "дня"

    async def text_handler(self, message: Message, state: FSMContext):
        current_data = await state.get_data()
        if message.text in self.db.get_courses_name():
            await state.update_data(course_id=self.db.get_course_id_by_name(message.text))
            delta = self.db.get_near_flow_delta_by_course_id(self.db.get_course_id_by_name(message.text))
            await message.answer(text=COURSE_TEXT.format(message.text[2:], delta, self.get_ending_word_day(delta)),
                                 reply_markup=self.buttons.in_course())
        elif message.text == self.buttons.description_btn.text:
            await message.answer(text=self.db.get_course_full_description(current_data['course_id']))
        elif message.text == self.buttons.program_btn.text:
            await self.bot.send_photo(chat_id=message.chat.id,
                                      photo=self.db.get_course_program(current_data['course_id']))
        elif message.text == self.buttons.buy_btn.text:

            await message.answer(text="❗Для оформления заявки заполните пресональные данные учащегося 👇")
            await message.answer(text="🔡 Введите ФИО учащегося")
            await PersonalInfo.fio.set()

            # await self.bot.send_invoice(chat_id=message.chat.id,
            #                        title=self.db.get_course_name(current_data['course_id']),
            #                        description=self.db.get_course_short_description(current_data['course_id']),
            #                        payload=f"Course|{current_data['course_id']}",
            #                        provider_token="381764678:TEST:38055",
            #                        currency="RUB",
            #                        start_parameter="course-payment",
            #                        prices=[LabeledPrice(label="Руб", amount=999 * 100)],
            #                        )
        elif message.text == self.buttons.back_to_courses_btn.text:
            await message.answer(text=COURSES_LIST,
                                 reply_markup=self.buttons.get_courses_buttons())
            await state.update_data(id=None)
        elif message.text == self.buttons.student_account_btn.text:
            await message.answer(text=STUDENT_START_TEXT.format(self.db.get_student_name_by_chat_id(message.chat.id)),
                                 reply_markup=self.buttons.get_flow_for_student(
                                     self.db.get_student_id_by_chat_id(message.chat.id)))
            await MainStates.student.set()
        else:
            await message.answer("К сожалению, я вас не понимаю 😢")

    async def personal_info(self, message: Message, state: FSMContext):
        cur_state = await state.get_state()
        data = await state.get_data()
        if message.text in [self.buttons.description_btn.text, self.buttons.program_btn.text, self.buttons.buy_btn.text,
                            self.buttons.back_to_courses_btn.text]:
            await self.text_handler(message, state)
        else:
            if cur_state == PersonalInfo.fio.state:
                await state.update_data(fio=message.text)
                await message.answer(text="📲 Введите номер телефона учащегося")
                await PersonalInfo.phone.set()
            elif cur_state == PersonalInfo.phone.state:
                await state.update_data(phone=message.text)
                await message.answer(text="🔑 Введите ник учащегося (без знака @)",
                                     reply_markup=self.buttons.how_find_username())
                await PersonalInfo.username.set()
            elif cur_state == PersonalInfo.username.state:
                await state.update_data(username=message.text.lower())
                corr_pi_msg = await message.answer(
                    text=CORRECTNESS_PERSONAL_INFO.format(data['fio'], data['phone'], message.text.lower()),
                    reply_markup=self.buttons.edit_personal_info())
                await state.update_data(corr_pi_msg=corr_pi_msg)
                await PersonalInfo.check_info.set()

    async def editing_personal_info(self, message: Message, state: FSMContext):
        cur_state = await state.get_state()
        if message.text in [self.buttons.description_btn.text, self.buttons.program_btn.text, self.buttons.buy_btn.text,
                            self.buttons.back_to_courses_btn.text]:
            await self.text_handler(message, state)
        else:
            if cur_state == PersonalInfo.edit_fio.state:
                await state.update_data(fio=message.text)
            elif cur_state == PersonalInfo.edit_phone.state:
                await state.update_data(phone=message.text)
            elif cur_state == PersonalInfo.edit_username.state:
                await state.update_data(username=message.text)

            data = await state.get_data()
            await self.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=data['corr_pi_msg'].message_id,
                text=CORRECTNESS_PERSONAL_INFO.format(data['fio'], data['phone'], data['username']),
                reply_markup=self.buttons.edit_personal_info())
            await message.answer("Данные успешно изменены!\n\nНажмите кнопку <b>Подтвердить</b> выше, если данные корректны 👆")

            await PersonalInfo.check_info.set()

    # async def pre_checkout_handler(self, pre_checkout: PreCheckoutQuery):
    #     await self.bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout.id, ok=True)

    # async def after_payment(self, message: Message, state: FSMContext):
    #     payload_info = message.successful_payment.invoice_payload.split("|")
    #     if payload_info[0] == 'Course':
    #         await message.answer(text=SUCCESSFUL_PAYMENT_TEXT.format(self.db.get_course_name(int(payload_info[1]))[2:]))
    #         await self.bot.send_message(chat_id=ID_RAFAIL,
    #                                text=SUCCESSFUL_PAYMENT_INFO_FOR_ADMIN.format(message.from_user.full_name,
    #                                                                              message.from_user.username,
    #                                                                              self.db.get_course_name(
    #                                                                                  int(payload_info[1]))[2:]),
    #                                reply_markup=self.buttons.get_buttons_after_payment())
    #         await state.reset_state()
