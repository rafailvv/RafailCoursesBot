from aiogram import *
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import  *
from asyncio import *

from buttons import Buttons
from constans import BOT_TOKEN, START_TEXT, COURSE_TEXT, COURSES_LIST, BUY_COURSE_TEXT, ID_RAFAIL, INFO_FOR_BUY_COURSE, \
    REJECTED_TEXT, ACCEPTED_TEXT
from database import Database

loop = get_event_loop()
bot = Bot(BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, loop, storage=MemoryStorage())

db = Database()
buttons = Buttons(db)

@dp.message_handler(commands=['start'])
async def start_message(message : Message):
    await bot.send_photo(chat_id=message.chat.id,
                         photo=open('image/rafail.png', 'rb'),
                         caption=START_TEXT.format(message.from_user.full_name),
                         reply_markup=buttons.get_courses_buttons())


@dp.callback_query_handler()
async def callback_handler(callback : CallbackQuery):
    data = callback.data.split("|")
    if data[0] == "Buy":
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        if data[1] == "Reject":
            await bot.send_message(chat_id=data[2], text=REJECTED_TEXT.format(db.get_course_name(data[3])[2:]))
        if data[1] == "Accept":
            await bot.send_message(chat_id=data[2], text=ACCEPTED_TEXT.format(db.get_course_name(data[3])[2:]))



@dp.message_handler(content_types=['text'])
async def text_handler(message : Message, state : FSMContext):
    current_data = await state.get_data()
    if message.text in db.get_courses_name():
        await state.update_data(course_id = db.get_course_id_by_name(message.text))
        await message.answer(text=COURSE_TEXT.format(message.text[2:], 2),
                             reply_markup=buttons.in_course())
    elif message.text == buttons.description_btn.text:
        await message.answer(text=db.get_course_description(current_data['course_id']))
    elif message.text == buttons.program_btn.text:
        await bot.send_photo(chat_id=message.chat.id,
                             photo=db.get_course_program(current_data['course_id']))
    elif message.text == buttons.buy_btn.text:
        await message.answer(text=BUY_COURSE_TEXT.format(db.get_course_name(current_data['course_id'])[2:]))
        await bot.send_message(chat_id=ID_RAFAIL,
                               text=INFO_FOR_BUY_COURSE.format(message.from_user.full_name,
                                                               message.from_user.username,
                                                               db.get_course_name(current_data['course_id'])[2:]),
                               reply_markup=buttons.get_confirm_and_reject(message.chat.id, current_data['course_id']))
    elif message.text == buttons.back_to_courses_btn.text:
        await message.answer(text=COURSES_LIST,
                             reply_markup=buttons.get_courses_buttons())
        await state.finish()


executor.start_polling(dp)
