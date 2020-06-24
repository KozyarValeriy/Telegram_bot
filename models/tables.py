from enum import Enum

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, create_engine, Integer

from config import DB_config


Base = declarative_base()


class BotTable(Base):
    """ Class for storing service information about users """
    __tablename__ = "bot_store"

    chat_id = Column(Integer, primary_key=True)
    mode = Column(Integer)
    lang = Column(Integer)

    def __repr__(self):
        return f"<BotTable(chat_id={self.chat_id}, mode={Mode(self.mode)}, lang={Lang(self.lang)})>"


class Lang(Enum):
    """ Class for enumerating languages """
    RU = 1
    EN = 2


class Mode(Enum):
    """ Class for enumerating modes """
    VOICE_TO_TEXT = 1
    TEXT_TO_VOICE = 2


if __name__ == "__main__":
    engine = create_engine(f"postgresql://{DB_config['user']}:{DB_config['password']}"
                           f"@{DB_config['host']}/{DB_config['dbname']}",
                           echo=True)
    Base.metadata.create_all(engine)
