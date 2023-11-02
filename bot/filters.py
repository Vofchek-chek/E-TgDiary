import sys

sys.path.append("../models/")
sys.path.append("../bot/")
sys.path.append("../config/")
from config import ADMINS
from aiogram.filters import Command, Filter
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)


class Text(Filter):
    def __init__(self, my_text: str) -> None:
        self.my_text = my_text

    async def __call__(self, message: Message) -> bool:
        return message.text == self.my_text


class Admin_command(Filter):
    def __init__(self, my_text: str) -> None:
        self.my_text = my_text

    async def __call__(self, message: Message) -> bool:
        return message.text == self.my_text and message.chat.id in ADMINS
