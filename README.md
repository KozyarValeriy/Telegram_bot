# Телеграм бот для преобразования текста в голос

## Инструкция для запуска

```bash
$ # Токен бота
$ export TOKEN=...
$ # Параметры для логирования
$ export BOT_LOG_LEVEL=INFO  # Один из {DEBUG, INFO, WARNING, ERROR, CRITICAL}. [по умолчанию: INFO]
$ # Активация виртуальной среды
$ python3 -m venv venv  # Создание виртуального окружения
$ source venv/bin/activate  # Активация виртуального окружения
$ pip3 install --upgrade pip  # Обновление pip
$ pip3 install -r requirements.txt  # Установка всех необходимых библиотек
$ # Для создания таблицы в базе для бота
$ python3 models/bot_service_table.py
$ # Для запуска бота
$ python3 bot.py
```
