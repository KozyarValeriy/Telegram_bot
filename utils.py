import os


def get_db_url() -> str:
    """ Function for getting URL for connecting to DB by sqlalchemy """
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL").replace("postgres://", "postgresql://")
    return "sqlite:///database.db?check_same_thread=false"
