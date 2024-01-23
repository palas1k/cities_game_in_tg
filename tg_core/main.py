import logging
import os
from datetime import datetime

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command

from tg_core.commands import set_commands
from tg_core.form import check_city, answer_city, start_game
from tg_core.statesform import StepsCityForm

bot = Bot(os.getenv('TG_TOKEN'))
admin = os.getenv("TG_ADMIN")
dp = Dispatcher()


async def with_bot_start(bot: Bot):
    await set_commands(bot)
    await bot.send_message(admin, f"Bot start {datetime.now()}")


async def start():
    logging.basicConfig(level=logging.INFO)
    dp.startup.register(with_bot_start)
    dp.message.register(start_game, Command(commands='cities'))
    dp.message.register(check_city, StepsCityForm.CHECK_CITY)
    dp.message.register(answer_city, StepsCityForm.GET_ANSWER)

    try:
        await dp.start_polling(bot)
    except Exception as ex:
        print(ex)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
    