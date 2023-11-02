import sys

sys.path.append("../models/")
sys.path.append("../bot/")
sys.path.append("../config/")
from sqlalchemy.orm import Session
from sqlalchemy import func, create_engine, select
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import (
    KeyboardBuilder,
    InlineKeyboardBuilder,
    ReplyKeyboardBuilder,
)
from models import Lesson, Base
from config import group_choosing_text


licence_agreemnt = InlineKeyboardBuilder()
licence_agreemnt.button(
    text="Лиц.соглашение",
    url="https://telegra.ph/Licenzionnoe-soglashenie-10-30",
)
licence_agreemnt = licence_agreemnt.as_markup()

setting_menu_markup = InlineKeyboardBuilder()
setting_menu_markup.button(
    text="👥Смена группы👥",
    callback_data="gr_change",
)
# setting_menu_markup.button(
#     text="Кастомизация",
#     callback_data="castomization",
# )
setting_menu_markup.button(
    text="⏰Авт.рассылка⏰",
    callback_data="scheduling",
)
setting_menu_markup.button(
    text="Лиц.соглашение",
    url="https://telegra.ph/Licenzionnoe-soglashenie-10-30",
)
setting_menu_markup.adjust(1, repeat=True)
setting_menu_markup = setting_menu_markup.as_markup()


scheduling_agreement = InlineKeyboardBuilder()
scheduling_agreement.button(
    text="🆗",
    callback_data="y sch",
)
scheduling_agreement.button(
    text="Описание работы ф-ий",
    url="https://telegra.ph/Opisanie-raboty-avtrassylki-10-29",
)
scheduling_agreement.button(
    text="⏰Выбрать время отправки⏰",
    callback_data="cst_t_chsng",
)
scheduling_agreement.button(
    text="⬅️Назад",
    callback_data="settings",
)
scheduling_agreement.adjust(1, repeat=True)
scheduling_agreement = scheduling_agreement.as_markup()


castomization_agreement = InlineKeyboardBuilder()
castomization_agreement.button(
    text="🆗",
    callback_data="y cast",
)
castomization_agreement.button(
    text="Описание работы кастомизации",
    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
)
castomization_agreement.button(
    text="⬅️Назад",
    callback_data="settings",
)
castomization_agreement.adjust(1, repeat=True)
castomization_agreement = castomization_agreement.as_markup()


global_sch_offspring = InlineKeyboardBuilder()
global_sch_offspring.button(
    text="⬅️Назад",
    callback_data="glob_diary",
)
global_sch_offspring = global_sch_offspring.as_markup()


class Diary_navigation_buttons:
    def __init__(self) -> None:
        self.buttons = {}
        self.groups = {}
        self.start_groups_list = InlineKeyboardBuilder()
        self.groups_list = InlineKeyboardBuilder()
        self.lazy_day = InlineKeyboardBuilder()
        self.default_menu = ReplyKeyboardBuilder()

    def get_start_groups_list(self) -> InlineKeyboardMarkup:
        return self.start_groups_list

    def get_groups_list(self) -> InlineKeyboardMarkup:
        return self.groups_list

    def get_default_menu(self) -> InlineKeyboardMarkup:
        return self.default_menu

    def check_group_existance(self, group: str) -> bool:
        return group in self.groups

    def get_cast_time_buttons(self, cur_date) -> InlineKeyboardMarkup:
        cast_time_buttons = InlineKeyboardBuilder()
        cast_time_buttons.row(
            InlineKeyboardButton(text="Часы", callback_data="txt"),
        )
        cast_time_buttons.row(
            InlineKeyboardButton(text="➖", callback_data="dec h"),
            InlineKeyboardButton(text="%s" % cur_date.hour, callback_data="txt"),
            InlineKeyboardButton(text="➕", callback_data="inc h"),
        )
        cast_time_buttons.row(
            InlineKeyboardButton(text="Минуты", callback_data="txt"),
        )
        cast_time_buttons.row(
            InlineKeyboardButton(text="➖", callback_data="dec m"),
            InlineKeyboardButton(text="%s" % cur_date.minute, callback_data="txt"),
            InlineKeyboardButton(text="➕", callback_data="inc m"),
        )
        cast_time_buttons.row(
            InlineKeyboardButton(text="⬅️Назад", callback_data="scheduling"),
        )
        return "Выберите время для отправки расписания", cast_time_buttons.as_markup()

    def create_buttons(self, session) -> None:
        tmp = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="🧾 Расписание"),
                    KeyboardButton(text="⚙️ Настройки"),
                    KeyboardButton(text="⏰ Авт.рассылка"),
                ]
            ],
            resize_keyboard=True,
        )
        self.default_menu = tmp

        self.lazy_day.button(text="Можно отдохнуть?", callback_data="txt Отдыхай)")
        self.lazy_day.button(text="Нужно!!!", callback_data="txt Отдыхай)")
        self.lazy_day.button(text="⬅️", callback_data="-1")
        self.lazy_day.button(text="➡️", callback_data="1")

        self.lazy_day.adjust(2, repeat=True)
        self.lazy_day = self.lazy_day.as_markup()

        for lesson_info in session.execute(
            select(Lesson).where(Lesson.up_to_date == True)
        ):
            lesson_info = lesson_info[0]
            lesson_info.date = lesson_info.date.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )

            lesson_info.group = lesson_info.group.split()[0]

            if lesson_info.group not in self.groups:
                self.groups[lesson_info.group] = {}

            if lesson_info.date not in self.groups[lesson_info.group]:
                self.groups[lesson_info.group][lesson_info.date] = []

            self.groups[lesson_info.group][lesson_info.date].append(lesson_info)

        for gr in sorted(set(self.groups.keys())):
            self.groups_list.button(
                text=gr,
                callback_data=gr,
            )
            self.start_groups_list.button(
                text=gr,
                callback_data=gr,
            )

        self.groups_list.button(text="⬅️Назад", callback_data="settings")
        self.groups_list.adjust(5, repeat=True)
        self.start_groups_list.adjust(5, repeat=True)
        self.groups_list = self.groups_list.as_markup()
        self.start_groups_list = self.start_groups_list.as_markup()

        pair_number = {
            9: "1️⃣",
            10: "2️⃣",
            13: "3️⃣",
            15: "4️⃣",
            16: "5️⃣",
            5: "6️⃣",
            6: "7️⃣",
        }

        for gr in self.groups:
            for day_date in self.groups[gr]:
                unpended_lessons = sorted(
                    self.groups[gr][day_date], key=lambda x: x.beginning_time
                )

                if gr not in self.buttons:
                    self.buttons[gr] = {}

                self.buttons[gr][day_date] = InlineKeyboardBuilder()
                row_num = 0
                for lesson in unpended_lessons:
                    self.buttons[gr][day_date].button(
                        text=pair_number[lesson.beginning_time.hour]
                        + " "
                        + lesson.subject_title,
                        callback_data="txt btn %s %s" % (row_num, 0),
                    )
                    row_num += 1
                    self.buttons[gr][day_date].button(
                        text=lesson.room,
                        callback_data="txt btn %s %s" % (row_num, 0),
                    )
                    self.buttons[gr][day_date].button(
                        text=lesson.teacher,
                        callback_data="txt btn %s %s" % (row_num, 1),
                    )
                    self.buttons[gr][day_date].button(
                        text="%s:%s-%s:%s"
                        % (
                            lesson.beginning_time.hour,
                            lesson.beginning_time.minute,
                            lesson.ending_time.hour,
                            lesson.ending_time.minute,
                        ),
                        callback_data="txt btn %s %s" % (row_num, 2),
                    )
                    row_num += 1

                self.buttons[gr][day_date].adjust(1, 3, repeat=True)
                self.buttons[gr][day_date].row(
                    InlineKeyboardButton(text="⬅️", callback_data="-1"),
                    InlineKeyboardButton(text="➡️", callback_data="1"),
                    width=2,
                )
                self.buttons[gr][day_date] = inline_keyboard = self.buttons[gr][
                    day_date
                ].as_markup()

    def get_diary_for_group(self, group_name: str, date) -> InlineKeyboardMarkup:
        weekday_to_str = {
            0: "Пн.",
            1: "Вт.",
            2: "Ср.",
            3: "Чт.",
            4: "Пт.",
            5: "Сб.",
            6: "Вс.",
        }
        if group_name in self.buttons:
            date = date.replace(tzinfo=None)
            if date in self.buttons[group_name]:
                return (
                    group_name
                    + "| "
                    + weekday_to_str[date.weekday()]
                    + "  "
                    + date.strftime("%d.%m.%y"),
                    self.buttons[group_name][date],
                )
            else:
                return (
                    group_name
                    + "| "
                    + weekday_to_str[date.weekday()]
                    + "  "
                    + date.strftime("%d.%m.%y"),
                    self.lazy_day,
                )
        else:
            return group_choosing_text, self.groups_list
