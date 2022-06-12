import asyncio
import logging

from aiogram import Bot, Dispatcher,executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from bot.buttons.buttons import Buttons
from bot.config import load_config
from bot.database.db import Database
from bot.handlers.callback import Callback
from bot.handlers.registration import Registration
from bot.handlers.start import Start
from bot.handlers.student import Student
from bot.handlers.teacher import Teacher

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    bot['config'] = config

    db = Database()
    buttons = Buttons(db)

    start = Start(bot, db, buttons, dp)
    Callback(bot, db, buttons, dp)
    Registration(bot, db, buttons, dp)
    Teacher(bot, db, buttons, dp)
    Student(bot, db, buttons, dp)

    await start.send_upsated_bot_message()

    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
