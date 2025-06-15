import logging

from aiogram import Bot

from bot.app import ADMINS


async def start_bot_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=admin, text='🤖🟩 Бот рабоотает!')
        except Exception as e:
            logging.exception(f"{e}: chatID({admin}) не найден!")


async def stop_bot_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=admin, text='🤖🟥 Бот выключен!')
        except Exception as e:
            logging.exception(f"{e}: chatID({admin}) не найден!")