import io
import os
import queue
import time

import telebot
from gtts import gTTS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from logger import get_logger
from models import BotTable, Lang
from photo import Photo
from string_constant import rus as str_const

# constants
TOKEN = os.getenv("TOKEN")
PHOTO_URL = "https://api.telegram.org/file/bot{0}/{1}"
LOADING = {"\\": "|", "|": "/", "/": "-", "-": "\\"}


bot = telebot.TeleBot(TOKEN)
log = get_logger(__name__)


@bot.message_handler(commands=['help'])
def handle_help(message):
    """ Handle for processing message /help """
    log.info("Handling /help")
    log.debug(str(message))
    bot.send_message(message.chat.id, str_const.help_message)


@bot.message_handler(commands=['start'])
def handle_start(message):
    """ Handle for processing message /start """
    log.info("Handling /start")
    log.debug(str(message))
    try:
        current_user = session.query(BotTable).filter(BotTable.chat_id == message.chat.id).first()
        # adding new user if not exist
        if current_user is None:
            user = BotTable(chat_id=message.chat.id, lang=Lang.RU.value)
            session.add(user)
            session.commit()
            # sending hello message
            bot.send_message(message.chat.id, str_const.hello_message)
        else:
            bot.send_message(message.chat.id, str_const.user_exists)

    except Exception as err:
        log.error(f"Some error occurred: {err}")
        bot.send_message(message.chat.id, str_const.error.format(err=str(err)))


@bot.message_handler(commands=['stop'])
def handle_stop(message):
    """ Handle for processing message /stop """
    log.info("Handling /stop")
    log.debug(str(message))
    try:
        current_user = session.query(BotTable).filter(BotTable.chat_id == message.chat.id).first()
        # deleting user if exist
        if current_user is None:
            session.delete(current_user)
            session.commit()
            # sending hello message
            bot.send_message(message.chat.id, str_const.farewell_msg)
        else:
            bot.send_message(message.chat.id, str_const.unauthorized)
    except Exception as err:
        log.error(f"Some error occurred: {err}")
        bot.send_message(message.chat.id, str_const.error.format(err=str(err)))


@bot.message_handler(commands=['set_lang', 'get_lang'])
def handle_lang(message):
    """ Handle for processing message /set_lang, /get_lang """
    log.info("Handling /set_lang, /get_lang")
    log.debug(str(message))
    try:
        current_user = session.query(BotTable).filter(BotTable.chat_id == message.chat.id).first()
        if current_user is None:
            bot.send_message(message.chat.id, str_const.unauthorized)
        if message.text == '/set_lang':
            # adding keyboard for lang choosing
            keyboard = telebot.types.InlineKeyboardMarkup()
            key_ru = telebot.types.InlineKeyboardButton(text=str_const.rus, callback_data='lang_ru')
            keyboard.add(key_ru)
            key_en = telebot.types.InlineKeyboardButton(text=str_const.eng, callback_data='lang_en')
            keyboard.add(key_en)
            bot.send_message(message.chat.id, text=str_const.change_lang, reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, str_const.current_lang.format(Lang(current_user.lang).name))
    except Exception as err:
        log.error(f"Some error occurred: {err}")
        bot.send_message(message.chat.id, str_const.error.format(err=str(err)))


@bot.message_handler(content_types=["voice"])
def repeat_audio_messages(message):
    """ Handle for processing voice message """
    log.info("Handling voice")
    log.debug(str(message))
    current_user = session.query(BotTable).filter(BotTable.chat_id == message.chat.id).first()
    if current_user is None:
        bot.send_message(message.chat.id, str_const.unauthorized)
    bot.send_message(message.chat.id, str_const.not_work)


@bot.message_handler(content_types=["text"])
def repeat_text_messages(message):
    """ Handle for processing text message """
    log.info("Handling text")
    log.debug(str(message))
    try:
        current_user = session.query(BotTable).filter(BotTable.chat_id == message.chat.id).first()
        if current_user is None:
            bot.send_message(message.chat.id, str_const.unauthorized)
        else:
            answer = io.BytesIO()
            audio_text = gTTS(text=message.text, lang=Lang(current_user.lang).name.lower(), slow=False)
            audio_text.write_to_fp(answer)
            answer.seek(0)
            bot.send_voice(message.chat.id, answer.read())
    except Exception as err:
        log.error(f"Some error occurred: {err}")
        bot.send_message(message.chat.id, str_const.error.format(err=str(err)))


@bot.message_handler(content_types=["photo"])
def repeat_text_messages(message):
    """ Handle for processing image in message """
    log.info("Handling photo")
    log.debug(str(message))
    try:
        start = time.perf_counter()
        bot.send_message(message.chat.id, str_const.info_msg_photo)
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        n_clusters = 3
        if message.caption is not None and message.caption.isdigit():
            n_clusters = int(message.caption)

        photo = Photo(url=PHOTO_URL.format(TOKEN, file_info.file_path), n_clusters=n_clusters)
        photo.start()

        current_loading_char = "\\"
        msg = bot.send_message(
            message.chat.id,
            str_const.image_processing.format(loading=current_loading_char, time=time.perf_counter()-start)
        )
        while True:
            try:
                result = photo.queue.get(timeout=0.5)
                break
            except queue.Empty:
                current_loading_char = LOADING[current_loading_char]
                bot.edit_message_text(
                    str_const.image_processing.format(loading=current_loading_char,
                                                      time=time.perf_counter()-start),
                    message.chat.id, msg.id
                )
        photo.join()
        bot.delete_message(message.chat.id, msg.id)
        bot.send_photo(
            message.chat.id,
            result,
            caption=str_const.info_msg_photo_processing.format(time.perf_counter()-start)
        )
    except Exception as err:
        log.error(f"Some error occurred: {err}")
        bot.send_message(message.chat.id, str_const.error.format(err=str(err)))


@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def change_settings(call):
    log.info("Handling keyboard for lang_")
    current_user = session.query(BotTable).filter(BotTable.chat_id == call.message.chat.id).first()
    if call.data.startswith("lang_"):
        # keyboard for changing lang
        if call.data.endswith("ru"):
            current_user.lang = Lang.RU.value
        elif call.data.endswith("en"):
            current_user.lang = Lang.EN.value
        session.commit()
        bot.send_message(call.message.chat.id, str_const.changed_lang.format(lang=Lang(current_user.lang).name))


if __name__ == '__main__':
    engine = create_engine("sqlite:///database.db?check_same_thread=false")
    Session = sessionmaker(bind=engine)
    session = Session()
    log.info("Starting bot")
    bot.polling(none_stop=True, interval=1)
