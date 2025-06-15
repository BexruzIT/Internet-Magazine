import logging

from aiogram import Bot
from aiogram.types import BotCommand


async def add_bot_commands(bot: Bot):
    commands = [
        BotCommand(command='start', description='Запустить бот'),
        BotCommand(command='help', description='Получить помщь'),
        BotCommand(command='about', description='О боте'),
        BotCommand(command='category', description='Посмотреть товары'),
        BotCommand(command='inline_mode', description='Функция поиска по вводу')
    ]
    await bot.set_my_commands(commands=commands)
    logging.info('Bot komadalari muvoffaqiyatli o`rnatildi!')