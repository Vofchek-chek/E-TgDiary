from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import MetaData, Column, BigInteger, Boolean, String
from sqlalchemy import URL
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from datetime import datetime


my_metadata = MetaData()


class Base(DeclarativeBase):
    metadata = my_metadata


class User(Base):
    __tablename__ = "tg_bot_users"

    _id = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    cur_date: Mapped[datetime]
    glob_date: Mapped[datetime]
    sch_date: Mapped[datetime]
    group = Column(String, nullable=True)
    is_bot = Column(Boolean, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    language_code = Column(String, nullable=True)
    is_premium = Column(Boolean, nullable=True)
    added_to_attachment_menu = Column(Boolean, nullable=True)
    can_join_groups = Column(Boolean, nullable=True)
    can_read_all_group_messages = Column(Boolean, nullable=True)
    supports_inline_queries = Column(Boolean, nullable=True)
    sch_agreement = Column(Boolean, default=False)
    cast_agreement = Column(Boolean, default=False)
    is_updated = Column(Boolean, default=True)


class Lesson(Base):
    __tablename__ = "diary"

    _id = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    faculty: Mapped[str]
    group: Mapped[str]
    subject_title: Mapped[str]
    teacher: Mapped[str]
    room: Mapped[str]  # Column(String, default=True)
    beginning_time: Mapped[datetime]
    ending_time: Mapped[datetime]
    date: Mapped[datetime]
    up_to_date = Column(Boolean, default=True)


class Media_storage(Base):
    __tablename__ = "media_data_storage"

    owner: Mapped[str] = mapped_column(primary_key=True)
    link: Mapped[str]


class Pended_files(Base):
    __tablename__ = "pended_diary_files"

    file_name: Mapped[str] = mapped_column(primary_key=True)
