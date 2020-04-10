"""
    Скрипт с ответами на шаблонные запросы.
"""

help_message = '''В зависимости от выбранного
режима работы бот либо преобразует текстовые сообщения в аудио, либо аудио
сообщения в текстовые

Управляющие команды:

/set_lang - смена языка
/get_lang - получение текущего языка
/set_mode - смена режима работы
/get_mode - получение текущего режима

Поддерживаемые языки:
    русский
    английский

Режимы работы:
    режим преобразования текстовых сообщений
    режим распозноваяния голосовый сообщений
'''

current_lang = "Текущий язык: {0}"

hello_message = "Привет! Для получения информации о работе бота просто отправте /help"