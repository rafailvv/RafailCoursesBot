from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, ContentTypes

from bot.buttons.buttons import Buttons
from bot.message_texts.constans import START_TEXT, COURSE_TEXT, COURSES_LIST, BUY_COURSE_TEXT, ID_RAFAIL, \
    INFO_FOR_BUY_COURSE, \
    REJECTED_TEXT, ACCEPTED_TEXT, SUCCESSFUL_PAYMENT_TEXT, SUCCESSFUL_PAYMENT_INFO_FOR_ADMIN, TEACHER_START_TEXT
from bot.database.db import Database
from bot.misc.states import States


class Registration:
    def __init__(self, bot : Bot, db : Database, buttons : Buttons, dp : Dispatcher):
        self.bot = bot
        self.db = db
        self.buttons = buttons
        dp.register_message_handler(self.start_message, commands=['start'], state="*")
        dp.register_callback_query_handler(self.registration_confirmation, state=States.registration)
        dp.register_message_handler(self.text_handler, state=States.registration)
        dp.register_pre_checkout_query_handler(self.pre_checkout_handler, state=States.registration)
        # dp.register_message_handler(self.after_payment, state=[registration], content_types=ContentTypes.SUCCESSFUL_PAYMENT)

    async def start_message(self, message : Message,state : FSMContext):
        if self.db.is_teacher(message.chat.id,message.from_user.username):
            await message.answer(text=TEACHER_START_TEXT.format(message.from_user.first_name),
                                 reply_markup=self.buttons.get_flow_for_teacher(self.db.get_teacher_id_by_chat_id(message.chat.id)))
            await state.update_data(flow_id = None)
            await States.teacher.set()
        else:
            await self.bot.send_photo(chat_id=message.chat.id,
                             photo=open('bot/image/rafail.png', 'rb'),
                             caption=START_TEXT.format(message.from_user.first_name),
                             reply_markup=self.buttons.get_courses_buttons())
            await state.update_data(course_id = None)
            await States.registration.set()




    async def registration_confirmation(self, callback: CallbackQuery, state : FSMContext):
        data = callback.data.split("|")
        print(data)
        if data[0] == "Buy":
            await self.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
            if data[1] == "Reject":
                await self.bot.send_message(chat_id=data[2], text=REJECTED_TEXT.format(self.db.get_course_name(data[3])[2:]))
            if data[1] == "Accept":
                await self.bot.send_message(chat_id=data[2], text=ACCEPTED_TEXT.format(self.db.get_course_name(data[3])[2:]))
                await state.reset_state()

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
            delta = self.db.get_near_flow_delta_by_course_id( self.db.get_course_id_by_name(message.text))
            await message.answer(text=COURSE_TEXT.format(message.text[2:], delta, self.get_ending_word_day(delta)),
                                 reply_markup=self.buttons.in_course())
        elif message.text == self.buttons.description_btn.text:
            await message.answer(text=self.db.get_course_full_description(current_data['course_id']))
        elif message.text == self.buttons.program_btn.text:
            await self.bot.send_photo(chat_id=message.chat.id,
                                 photo=self.db.get_course_program(current_data['course_id']))
        elif message.text == self.buttons.buy_btn.text:
            await message.answer(text=BUY_COURSE_TEXT.format(self.db.get_course_name(current_data['course_id'])[2:]))
            await self.bot.send_message(chat_id=ID_RAFAIL,
                               text=INFO_FOR_BUY_COURSE.format(message.from_user.full_name,
                                                               message.from_user.username,
                                                               self.db.get_course_name(current_data['course_id'])[2:]),
                               reply_markup=self.buttons.get_confirm_and_reject(message.chat.id, current_data['course_id']))
            # await self.bot.send_invoice(chat_id=message.chat.id,
            #                        title=self.db.get_course_name(current_data['course_id']),
            #                        description=self.db.get_course_short_description(current_data['course_id']),
            #                        payload=f"Course|{current_data['course_id']}",
            #                        provider_token="381764678:TEST:38055",
            #                        currency="RUB",
            #                        start_parameter="course-payment",
            #                        prices=[LabeledPrice(label="Руб", amount=999 * 100)],
            #                        )
        elif message.text ==self.buttons.back_to_courses_btn.text:
            await message.answer(text=COURSES_LIST,
                                 reply_markup=self.buttons.get_courses_buttons())
            await state.update_data(id = None)
        else:
            await message.answer("К сожалению, я вас не понимаю 😢")

    async def pre_checkout_handler(self, pre_checkout: PreCheckoutQuery):
        await self.bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout.id, ok=True)

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