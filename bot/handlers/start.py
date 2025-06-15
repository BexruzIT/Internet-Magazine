from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton
from aiogram import Router, html
from aiogram.utils.keyboard import InlineKeyboardBuilder

start_router = Router()


@start_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}!\n\n"
                         f"Напишите /category, чтобы просмотреть продукты.")


@start_router.message(Command('inline_mode'))
async def command_start_handler(message: Message) -> None:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🔍 Поиск слов",
            switch_inline_query="kitob"  # Bu inputda @bot_username kitob ko'rinishida paydo bo'ladi
        ),
        InlineKeyboardButton(
            text="🔍 Поиск из бота",
            switch_inline_query_current_chat="iphone"  # Bu inputda @bot_username kitob ko'rinishida paydo bo'ladi
        )
    )
    await message.answer(f"Нажмите кнопку, чтобы использовать функцию поиска во встроенном режиме.",
                         reply_markup=builder.as_markup())