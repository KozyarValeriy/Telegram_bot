import os


def get_db_url() -> str:
    """ Function for getting URL for connecting to DB by sqlalchemy """
    return os.getenv("DATABASE_URL", "sqlite:///database.db?check_same_thread=false")
