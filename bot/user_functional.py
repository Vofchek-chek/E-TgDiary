from typing import Optional
from sqlalchemy import update, insert
from datetime import datetime, timedelta
from models import Base, User, Media_storage


class Interaction:
    def __init__(self) -> None:
        pass

    def create_connection(self, session):
        self.session = session

    def check_user_for_existance(self, user_id: int) -> bool:
        return self.session.query(User._id).filter_by(_id=user_id).first() is not None

    def get_cur_sch_time(self, user_id: int) -> datetime:
        return self.session.query(User.sch_date).filter_by(_id=user_id).first()[0]

    def update_user_date(self, user_id: int, new_date: datetime) -> bool:
        result = self.session.execute(
            update(User)
            .where(User._id == user_id)
            .values(glob_date=new_date, cur_date=new_date)
        )
        self.session.commit()
        return bool(result.rowcount)

    def change_cur_sch_time(self, user_id: int, new_sch_date: datetime) -> bool:
        result = self.session.execute(
            update(User).where(User._id == user_id).values(sch_date=new_sch_date)
        )
        self.session.commit()
        return bool(result.rowcount)

    def check_user_for_updates(self, user_id: int) -> bool:
        return self.session.query(User.is_updated).filter_by(_id=user_id).first()[0]

    def set_user_up_to_date(self, user_id: int) -> bool:
        result = self.session.execute(
            update(User).where(User._id == user_id).values(is_updated=True)
        )
        self.session.commit()
        return bool(result.rowcount)

    def add_user_to_db(self, user: User) -> None:
        if self.session.query(User.group).filter_by(_id=user._id).first() is None:
            self.session.add(user)
            self.session.commit()

    def get_user_group_info(self, user_id: int) -> str:
        result = self.session.query(User.group).filter_by(_id=user_id).first()

        if result is not None:
            return result[0]
        else:
            return ""

    def set_group(self, user_id: int, group: str) -> bool:
        result = self.session.execute(
            update(User).where(User._id == user_id).values(group=group)
        )
        self.session.commit()
        return bool(result.rowcount)

    def get_object_media(self, object_name: str) -> str:
        return (
            self.session.query(Media_storage.owner)
            .filter_by(owner=teacher_name)
            .first()
        )

    def get_cur_scheduling_settings_status(self, user_id: int) -> bool:
        return self.session.query(User.sch_agreement).filter_by(_id=user_id).first()[0]

    def change_scheduling_settings(self, user_id: int) -> bool:
        cur_settings = (
            self.session.query(User.sch_agreement).filter_by(_id=user_id).first()[0]
        )
        result = self.session.execute(
            update(User)
            .where(User._id == user_id)
            .values(sch_agreement=not cur_settings)
        )
        self.session.commit()

        return bool(result.rowcount)

    def add_media_to_object(self, object_name: str, media_link: str) -> None:
        pass

    def get_cur_user_page_date(self, user_id: int):
        return self.session.query(User.cur_date).filter_by(_id=user_id).first()[0]

    def get_cur_user_global_date(self, user_id: int):
        return self.session.query(User.glob_date).filter_by(_id=user_id).first()[0]

    def inc_cur_user_page_date(self, user_id: int):
        result = (
            self.session.query(User.cur_date, User.glob_date)
            .filter_by(_id=user_id)
            .first()
        )

        if result[0].isocalendar().week != result[1].isocalendar().week:
            result = result[1]
        else:
            result = result[0]

        if result.weekday() < 5:
            new_date = result + timedelta(days=1)
        else:
            new_date = result - timedelta(days=5)

        self.session.execute(
            update(User).where(User._id == user_id).values(cur_date=new_date)
        )

        self.session.commit()

        return new_date

    def dec_cur_user_page_date(self, user_id: int):
        result = self.session.query(User.cur_date).filter_by(_id=user_id).first()[0]
        if result.weekday() > 0:
            new_date = result - timedelta(days=1)
        else:
            new_date = result + timedelta(days=5)

        self.session.execute(
            update(User).where(User._id == user_id).values(cur_date=new_date)
        )

        self.session.commit()

        return new_date
