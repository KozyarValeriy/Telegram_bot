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
    
Дополнительные фичи:
    Если отпрвить фото, то бот переделает фото на указанное кол-во цветов (без указагия - 3 цвета)
    Для указания кол-ва цветов просто передайте чило в подписи фото (число должно быть больше нуля)
'''

farewell_msg = "Текущий пользователь удален из базы"

error = "Произошла ошибка. Для началоа работы бота необходимо отправить /start"

current_lang = "Текущий язык: {0}"

hello_message = "Привет! Для получения информации о работе бота просто отправте /help"

info_msg_photo = "Время обработки зависит от размера фотографии и требуемого кол-ва цветов. " \
                 "В среднем не более 15-20 секунд"

info_msg_photo_processing = "Обработка заняла: {0:2.1f} секунд"
