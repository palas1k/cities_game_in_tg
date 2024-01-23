from aiogram import Bot
from aiogram.types import BotCommand


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='cities',
            description='Поиграем в города'
        )]

    await bot.set_my_commands(commands)
