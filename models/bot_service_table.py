from enum import Enum

from sqlalchemy import Column, create_engine, Integer
from sqlalchemy.ext.declarative import declarative_base

from utils import get_db_url

Base = declarative_base()


class BotTable(Base):
    """ Class for storing service information about users """
    __tablename__ = "bot_store"

    chat_id = Column(Integer, primary_key=True)
    lang = Column(Integer)

    def __repr__(self):
        return f"<BotTable(chat_id={self.chat_id}, lang={Lang(self.lang)})>"


class Lang(Enum):
    """ Class for enumerating languages """
    RU = 1
    EN = 2


if __name__ == "__main__":
    engine = create_engine(get_db_url(), echo=True)
    Base.metadata.create_all(engine)
