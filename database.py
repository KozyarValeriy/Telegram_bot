"""
    Класс для получения коннекта к БД
"""

import psycopg2
import logging


_DB_TABLE = dict(table='telegram_bot', id='chat_id', mode='mode', lang='lang')

logging.basicConfig(filename="database.log", level=logging.ERROR, filemode="w")


class SingletonDB:
    """ Класс для получения коннекта к БД
        Соединение всегда одно и тоже.
    >>> from config import DB_config
    >>> data1 = SingletonDB(DB_config)
    >>> data2 = SingletonDB(DB_config)
    >>> data1 is data2
    True
    """
    _instance = None  # Текущий экземпляр класса
    config = None
    connect_to_DB = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config):
        """ Метод инициализации экземпляра

        :param config: словарь, содержащий ключи: dbname, user, password, host для подключения к БД.
        """
        if self.config is None:
            self.config = config
            try:
                self.connect_to_DB = psycopg2.connect(**self.config)
            except Exception as err:
                print('Error in connect to DB.')
                logging.error(err)

    def add_new_user(self, chat_id: int, mode: int, lang: int):
        """ Метод для добавления нового пользователя в базу данных

        :param chat_id: id чата, для которого идет настройка,
        :param mode: режим работы бота,
        :param lang: язык работы бота.
        """
        select_1 = f"select * from {_DB_TABLE['table']} where {_DB_TABLE['id']} = {chat_id}"
        insert = f"insert into {_DB_TABLE['table']} values ({chat_id}, {mode}, {lang})"
        try:
            with self.connect_to_DB.cursor() as cursor:
                cursor.execute(select_1)
                answer = cursor.fetchone()
                if answer is None:
                    # если такого пользователя еще нет
                    cursor.execute(insert)
            self.commit()
        except Exception as err:
            logging.error(err)

    def update(self, chat_id: int, update_param: str, new_value: int):
        """ Метод для смены режима работы пользователя

        :param chat_id: id чата, для которого идет настройка,
        :param update_param: параметр, который обновляется, один из ['mode', 'lang']
        :param new_value: новый режи работы.
        """
        param = _DB_TABLE.get(update_param)
        if param is None:
            print('Error key!')
            return
        select = f"select * from {_DB_TABLE['table']} where {_DB_TABLE['id']} = {chat_id}"
        update = f"update {_DB_TABLE['table']} set {_DB_TABLE[update_param]} = {new_value} " \
                 f"where {_DB_TABLE['id']} = {chat_id}"
        try:
            with self.connect_to_DB.cursor() as cursor:
                cursor.execute(select)
                answer = cursor.fetchone()
                if answer is None:
                    # если такого пользователя нет, то добавляем
                    self.add_new_user(chat_id, 1, 1)
                cursor.execute(update)
            self.commit()
        except Exception as err:
            logging.error(err)

    def get_user(self, chat_id: int) -> dict or None:
        """ Метод для получения пользователя по id чата

        :param chat_id: id чата, для которого требуется получить информацию
        :return: словавь вида {"chat_id": ..., "mode": ..., "lang": ...} или None, если такого пользователя нет
        """
        result = None
        select = f"select * from {_DB_TABLE['table']} where {_DB_TABLE['id']} = {chat_id}"
        try:
            with self.connect_to_DB.cursor() as cursor:
                cursor.execute(select)
                answer = cursor.fetchone()
                if answer is not None:
                    # если есть такой пользователь, то возвращаем словарь
                    result = dict(chat_id=answer[0], mode=answer[1], lang=answer[2])
        except Exception as err:
            logging.error(err)
        return result

    def commit(self):
        """ Метод для принятия изменения в БД """
        if self.connect_to_DB is not None:
            self.connect_to_DB.commit()

    def rollback(self):
        """ Метод для отката изменений в БД """
        if self.connect_to_DB is not None:
            self.connect_to_DB.rollback()

    def close(self):
        """ Метод для закрытия соединения с БД """
        if self.connect_to_DB is not None:
            self.connect_to_DB.close()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
