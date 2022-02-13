# Телеграм бот

## Описание
Бот позволяет преобразовывать текстовые сообщения в голосовые, а также изменять количество цветов в фотографии.

## Инструкция для запуска
Бот асинхронный, поэтому url для базы данных необходимо использовать с асинхронной библиотекой (например, asyncpg)
```bash
$ # Токен бота
$ export TOKEN=...
$ export DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:<post>/<db_name>
$ # Параметры для логирования
$ export BOT_LOG_LEVEL=INFO  # Один из {DEBUG, INFO, WARNING, ERROR, CRITICAL}. [по умолчанию: INFO]
$ # Активация виртуальной среды
$ python3 -m venv venv  # Создание виртуального окружения
$ source venv/bin/activate  # Активация виртуального окружения
$ pip3 install --upgrade pip  # Обновление pip
$ pip3 install -r requirements.txt  # Установка всех необходимых библиотек
$ # Для создания таблицы в базе для бота
$ # Сначала нужно добавить url для базы данных для alembic в файле alembic.ini в параметр sqlalchemy.url
$ # url для alembic должен использовать синхронную библиотеку (например, psycopg2)
$ # Затем выполнить команду:
$ alembic upgrade head
$ # Для запуска бота
$ nohup python3 bot.py &
```
