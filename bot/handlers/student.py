from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from bot.buttons.buttons import Buttons
from bot.database.db import Database
from bot.message_texts.constans import STUDENT_START_TEXT
from bot.misc.states import MainStates


class Student:
    def __init__(self, bot: Bot, db: Database, buttons: Buttons, dp: Dispatcher):
        self.bot = bot
        self.db = db
        self.buttons = buttons
        dp.register_message_handler(self.text_handler, state=MainStates.student)

    def text_handler(self, message : Message):
        pass
