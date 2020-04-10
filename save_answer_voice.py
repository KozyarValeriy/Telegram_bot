"""
    Скрипт с классом для сохранения ответа в строку байт
"""


class Sound:
    """ Класс для сохранения строки байт """

    def __init__(self):
        self.data = []

    def write(self, chunk: bytes):
        """ Метод для записи для подстановки вместо файла """
        self.data.append(chunk)

    def get_data(self) -> bytes:
        """ Метод для получения строки байт """
        return b''.join(self.data)
