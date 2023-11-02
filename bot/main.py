import asyncio
import pytz
import sys

sys.path.append("../models/")
sys.path.append("../config/")
sys.path.append("../update_notes/")
from models import User
from config import (
    greeting_text,
    local_url_object,
    group_choosing_text,
    TOKEN,
    licence_text,
    ADMINS,
)
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, Filter
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, update, select, insert
from datetime import datetime, timezone, timedelta
from user_functional import Interaction
from keyboards import (
    Diary_navigation_buttons,
    setting_menu_markup,
    scheduling_agreement,
    castomization_agreement,
    licence_agreemnt,
)
from models import User
from filters import Text, Admin_command
from update_news import make_updates


bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

ob = Diary_navigation_buttons()

users_db = Interaction()

timezone_offset = 0.0  # Pacific Standard Time (UTC−08:00)
tzinfo = timezone(timedelta(hours=timezone_offset))


@dp.message(Admin_command("/id"))
async def content_id(message: types.Message):
    print(dir(message))


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """

    possible_ref_link = (
        None if (len(txt_split := message.text.split()) == 1) else txt_split[-1]
    )

    text = None
    reply_markup = None

    if not users_db.check_user_for_existance(user_id=message.chat.id) or (
        not users_db.get_user_group_info(message.chat.id)
    ):
        user_info = message.from_user.__dict__
        user_info["_id"] = user_info["id"]
        del user_info["id"]
        user_info["group"] = (
            users_db.get_user_group_info(int(possible_ref_link))
            if (possible_ref_link and possible_ref_link.isdigit())
            else ""
        )
        tz = pytz.timezone("Asia/Tashkent")
        date = datetime.now(tz)

        date = date.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        user_info["cur_date"] = date
        user_info["glob_date"] = date
        user_info["sch_date"] = date + timedelta(
            days=1,
            hours=8,
            minutes=30,
        )

        users_db.add_user_to_db(User(**user_info))

        if users_db.get_user_group_info(message.chat.id):
            text, reply_markup = ob.get_diary_for_group(
                group_name=users_db.get_user_group_info(message.chat.id),
                date=date,
            )
        else:
            await bot.send_message(
                chat_id=message.chat.id,
                text=licence_text,
                reply_markup=licence_agreemnt,
                parse_mode=ParseMode.HTML,
            )
            text = greeting_text
            reply_markup = ob.get_start_groups_list()

    else:
        text, reply_markup = ob.get_diary_for_group(
            group_name=users_db.get_user_group_info(message.chat.id),
            date=users_db.get_cur_user_global_date(message.chat.id),
        )

    if text:
        await bot.send_message(
            chat_id=message.chat.id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
        )

    if not users_db.check_user_for_updates(message.chat.id):
        users_db.set_user_up_to_date(chat_id)
        await make_updates(message, ob.get_default_menu())


@dp.callback_query()
async def callback_answer(callback: types.CallbackQuery):
    data = callback.data
    chat_id = callback.message.chat.id

    if not users_db.check_user_for_updates(chat_id):
        users_db.set_user_up_to_date(chat_id)
        await make_updates(callback.message, ob.get_default_menu())

    if ob.check_group_existance(data):
        users_db.set_group(chat_id, data)
        await callback.answer(text="Группа успешно установлена!", alert=True)
        await callback.message.delete()
        await bot.send_message(
            text="Продолжим ?",
            chat_id=chat_id,
            reply_markup=ob.get_default_menu(),
            parse_mode=ParseMode.HTML,
        )
        return

    elif data == "1":
        date = users_db.inc_cur_user_page_date(chat_id)
        text, reply_markup = ob.get_diary_for_group(
            group_name=users_db.get_user_group_info(chat_id),
            date=date,
        )

        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup,
        )

    elif data == "-1":
        date = users_db.dec_cur_user_page_date(chat_id)
        text, reply_markup = ob.get_diary_for_group(
            group_name=users_db.get_user_group_info(chat_id),
            date=date,
        )

        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup,
        )

    elif data == "settings":
        await callback.message.edit_text(
            text="⚙️Настройки⚙️",
            reply_markup=setting_menu_markup,
        )

    elif data == "gr_change":
        await callback.message.edit_text(
            text="Выберите группу:",
            reply_markup=ob.get_groups_list(),
        )

    elif data == "castomization":
        await callback.message.edit_text(
            text="""
Активировать кастомное оформление чата от бота?
(подробнее с механникой можно ознакомитсья по ссылке снизу) 
            """,
            reply_markup=castomization_agreement,
        )

    elif data == "scheduling":
        cur_sch_status = users_db.get_cur_scheduling_settings_status(chat_id)
        await callback.message.edit_text(
            text="""
%sктивировать ежедневную рассылку расписания от бота?
(каждый день в 8:30 утра наш бот%sбудет отправлять вам расписание на день,
однако вы можете выбрать своё время:) ) 
            """
            % (("А", "Деа")[cur_sch_status], (" ", " не ")[cur_sch_status]),
            reply_markup=scheduling_agreement,
        )
    elif data == "cst_t_chsng":
        text, reply_markup = ob.get_cast_time_buttons(
            users_db.get_cur_sch_time(chat_id)
        )
        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup,
        )

    elif data == "glob_diary":
        pass

    elif data == "loc_diary":
        pass

    else:
        match data.split():
            case ["txt", "btn", row_num, button_num]:
                await callback.answer(
                    text=callback.message.reply_markup.inline_keyboard[int(row_num)][
                        int(button_num)
                    ].text,
                    alert=True,
                )
            case ["y", "sch"]:
                users_db.change_scheduling_settings(chat_id)
                await callback.answer(text="Изменения успешно внесены!", alert=True)
                await callback.message.edit_text(
                    text="Изменения успешно внесены!\nПродолжим ?",
                    reply_markup=None,
                    parse_mode=ParseMode.HTML,
                )
            case ["inc", t_obj]:
                prev_sch_time = users_db.get_cur_sch_time(chat_id)
                new_sch_time = prev_sch_time + timedelta(
                    hours=1 if t_obj == "h" else 0, minutes=5 if t_obj == "m" else 0
                )
                users_db.change_cur_sch_time(
                    chat_id,
                    prev_sch_time.replace(
                        hour=new_sch_time.hour,
                        minute=new_sch_time.minute,
                    ),
                )

                text, reply_markup = ob.get_cast_time_buttons(
                    users_db.get_cur_sch_time(chat_id)
                )
                await callback.message.edit_text(
                    text=text,
                    reply_markup=reply_markup,
                )

            case ["dec", t_obj]:
                prev_sch_time = users_db.get_cur_sch_time(chat_id)
                new_sch_time = prev_sch_time - timedelta(
                    hours=1 if t_obj == "h" else 0, minutes=5 if t_obj == "m" else 0
                )
                users_db.change_cur_sch_time(
                    chat_id,
                    prev_sch_time.replace(
                        hour=new_sch_time.hour,
                        minute=new_sch_time.minute,
                    ),
                )

                text, reply_markup = ob.get_cast_time_buttons(
                    users_db.get_cur_sch_time(chat_id)
                )
                await callback.message.edit_text(
                    text=text,
                    reply_markup=reply_markup,
                )


@dp.message(Text("🧾 Расписание"))
async def defult_menu_diary_answer(message: Message):
    chat_id = message.chat.id
    if not users_db.check_user_for_existance(user_id=chat_id):
        await send_welcome(message)
        return

    if not users_db.check_user_for_updates(chat_id):
        users_db.set_user_up_to_date(chat_id)
        await make_updates(message, ob.get_default_menu())

    date = users_db.get_cur_user_global_date(chat_id)

    text, reply_markup = ob.get_diary_for_group(
        group_name=users_db.get_user_group_info(chat_id),
        date=date,
    )

    await bot.send_message(
        text=text,
        chat_id=chat_id,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML,
    )


@dp.message(Text("⚙️ Настройки"))
async def defult_menu_settings_answer(message: Message):
    chat_id = message.chat.id
    if not users_db.check_user_for_existance(user_id=chat_id):
        await send_welcome(message)
        return

    if not users_db.check_user_for_updates(chat_id):
        users_db.set_user_up_to_date(chat_id)
        await make_updates(message, ob.get_default_menu())

    await bot.send_message(
        chat_id=chat_id,
        text="⚙️Настройки⚙️",
        reply_markup=setting_menu_markup,
        parse_mode=ParseMode.HTML,
    )


@dp.message(Text("⏰ Авт.рассылка"))
async def defult_menu_scheduling_answer(message: Message):
    chat_id = message.chat.id
    if not users_db.check_user_for_existance(user_id=chat_id):
        await send_welcome(message)
        return

    if not users_db.check_user_for_updates(chat_id):
        users_db.set_user_up_to_date(chat_id)
        await make_updates(message, ob.get_default_menu())

    cur_sch_status = users_db.get_cur_scheduling_settings_status(chat_id)

    await bot.send_message(
        chat_id=chat_id,
        text="""
%sктивировать ежедневную рассылку расписания от бота?
(каждый день в 8:30 утра наш бот%sбудет отправлять вам расписание на день) 
            """
        % (("А", "Деа")[cur_sch_status], (" ", " не ")[cur_sch_status]),
        reply_markup=scheduling_agreement,
        parse_mode=ParseMode.HTML,
    )


@dp.message()
async def defult_menu_scheduling_answer(message: Message):
    chat_id = message.chat.id
    if not users_db.check_user_for_existance(user_id=chat_id):
        await send_welcome(message)
        return

    if not users_db.check_user_for_updates(chat_id):
        users_db.set_user_up_to_date(chat_id)
        await make_updates(message, ob.get_default_menu())


async def main():
    engine = create_engine(local_url_object)
    with Session(engine) as session:
        users_db.create_connection(session)
        ob.create_buttons(session)
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
