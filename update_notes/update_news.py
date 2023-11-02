from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)


async def make_updates(message: Message, new_keyboard):
    update_info = """
Бот немного обновился) 
Из важного:
-отлажена авт.рассылка
-немного изменём дизайн
-обновлён функционал некоторых кнопок
-добавлена возможно устанавливать своё время для отправки расписания
подробнее тут:
https://telegra.ph/Obnovleniya-10-31
"""
    await message.answer(
        text=update_info,
        reply_markup=new_keyboard,
    )
