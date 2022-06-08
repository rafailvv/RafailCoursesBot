from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from bot.buttons.buttons import Buttons
from bot.database.db import Database
from bot.misc.states import MainStates


class Strdent:
    def __init__(self, bot: Bot, db: Database, buttons: Buttons, dp: Dispatcher):
        self.bot = bot
        self.db = db
        self.buttons = buttons
        # dp.register_message_handler(self., state=States.student)