import asyncio
import sys
import logging
import pytz

sys.path.append("../models/")
sys.path.append("../bot/")
sys.path.append("../config/")
from keyboards import (
    Diary_navigation_buttons,
    setting_menu_markup,
    scheduling_agreement,
    castomization_agreement,
)
from config import local_url_object, TOKEN
from models import User
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import update, select
from datetime import timedelta, datetime
from time import sleep
from aiogram import Bot
from aiogram.enums import ParseMode


bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

logging.basicConfig(
    filename="logs.log", filemode="a", format="%(name)s - %(levelname)s - %(message)s"
)


async def main(session):
    fresh_ob = Diary_navigation_buttons()
    fresh_ob.create_buttons(session)
    while True:
        tz = pytz.timezone("Asia/Tashkent")
        cur_nptime = datetime.now(tz).replace(tzinfo=None)
        for row in session.execute(select(User)):
            row = row[0]
            cur_time = cur_nptime.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )

            if row.glob_date < cur_time:
                date = row.glob_date + timedelta(days=1)

                session.execute(
                    update(User).where(User._id == row._id).values(glob_date=date)
                )
                session.commit()

            if row.sch_date < cur_nptime:
                text, reply_markup = fresh_ob.get_diary_for_group(
                    group_name=row.group,
                    date=row.glob_date,
                )

                if row.sch_agreement:
                    try:
                        await bot.send_message(
                            chat_id=row._id, text=text, reply_markup=reply_markup
                        )
                        sleep(0.05)
                    except Exception as e:
                        logging.error(e)

                date = row.sch_date + timedelta(days=1)

                session.execute(
                    update(User).where(User._id == row._id).values(sch_date=date)
                )
                session.commit()

        sleep(10)


if __name__ == "__main__":
    engine = create_engine(local_url_object)
    with Session(engine) as session:
        asyncio.run(main(session))
