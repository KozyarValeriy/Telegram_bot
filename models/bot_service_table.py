from enum import Enum
from typing import Optional

from sqlalchemy import Column, create_engine, Integer, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from utils import get_db_url

Base = declarative_base()


class BotTable(Base):  # type: ignore
    """ Class for storing service information about users """
    __tablename__ = "bot_store"

    chat_id = Column(Integer, primary_key=True)
    lang = Column(Integer)
    processed_dttm = Column(TIMESTAMP, onupdate=func.now(), default=func.now())

    def __repr__(self):
        return f"<BotTable(chat_id={self.chat_id}, lang={Lang(self.lang)})>"

    @classmethod
    def get_chat(cls, chat_id: str, session: Session) -> Optional["BotTable"]:
        """ Function for getting chat from db

        :param chat_id: chat id for searching chat in db,
        :param session: session for query into db,
        :return: BotTable instance or None
        """
        chat = session \
            .query(cls) \
            .filter_by(chat_id=chat_id) \
            .first()
        return chat


class Lang(Enum):
    """ Class for enumerating languages """
    RU = 1
    EN = 2


if __name__ == "__main__":
    engine = create_engine(get_db_url(), echo=True)
    Base.metadata.create_all(engine)
