import pprint
import json
import io
import time

from gtts import gTTS
import telebot
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from models.tables import BotTable, Lang, Mode
from config import DB_config, TOKEN
from string_constant import rus as str_const
from photo import Photo

bot = telebot.TeleBot(TOKEN)

PHOTO_URL = "https://api.telegram.org/file/bot{0}/{1}"


def print_message(msg):
    try:
        pprint.pprint(
            json.loads(str(msg)
                       .replace("'", '"')
                       .replace('False', 'false')
                       .replace('True', 'true')
                       .replace('None', 'null')
                       )
        )
    except json.decoder.JSONDecodeError:
        print(msg)


@bot.message_handler(commands=['help', 'start', 'stop', 'set_lang', 'get_lang', 'set_mode', 'get_mode'])
def handle_start_help(message):
    try:
        current_user = session.query(BotTable).filter(BotTable.chat_id == message.chat.id).first()
        if message.text == '/help':
            bot.send_message(message.chat.id, str_const.help_message)
        elif message.text == '/start':
            # отправляем приветсвенное сообщение
            bot.send_message(message.chat.id, str_const.hello_message)
            # добавление в базу нового чата
            if current_user is None:
                user = BotTable(chat_id=message.chat.id, mode=Mode.TEXT_TO_VOICE.value, lang=Lang.RU.value)
                session.add(user)
                session.commit()

        elif message.text == '/stop':
            if current_user is not None:
                bot.send_message(message.chat.id, str_const.farewell_msg)
                session.delete(current_user)
                session.commit()

        elif message.text == '/set_lang':
            # bot.send_message(message.chat.id, f'Текущий язык: {Lang(current_user.lang).name}')

            # Добавление клавиатуры для выбора языка
            keyboard = telebot.types.InlineKeyboardMarkup()
            key_ru = telebot.types.InlineKeyboardButton(text='Русский', callback_data='lang_ru')
            keyboard.add(key_ru)
            key_en = telebot.types.InlineKeyboardButton(text='Английский', callback_data='lang_en')
            keyboard.add(key_en)
            bot.send_message(message.chat.id, text='Выберите язык:', reply_markup=keyboard)

        elif message.text == '/get_lang':
            bot.send_message(message.chat.id, f'Текущий язык: {Lang(current_user.lang).name}')

        elif message.text == '/set_mode':
            # bot.send_message(message.chat.id, f'Текущий режим: {Mode(current_user.mode).name}')

            # Добавление клавиатуры для выбора языка
            keyboard = telebot.types.InlineKeyboardMarkup()
            key_mode_1 = telebot.types.InlineKeyboardButton(text='Голос в текст', callback_data='mode_1')
            keyboard.add(key_mode_1)
            key_mode_2 = telebot.types.InlineKeyboardButton(text='Текст в голос', callback_data='mode_2')
            keyboard.add(key_mode_2)
            bot.send_message(message.chat.id, text='Выбериет режим:', reply_markup=keyboard)

        elif message.text == '/get_mode':
            bot.send_message(message.chat.id, f'Текущий режим: {Mode(current_user.mode).name}')

    except AttributeError:
        bot.send_message(message.chat.id, str_const.error)


@bot.message_handler(content_types=["voice"])
def repeat_audio_messages(message):
    current_user = session.query(BotTable).filter(BotTable.chat_id == message.chat.id).first()
    if current_user.mode == Mode.VOICE_TO_TEXT.value:
        bot.send_message(message.chat.id, 'Пока не работает, скоро будет')
    print(message)


@bot.message_handler(content_types=["text"])
def repeat_text_messages(message):
    current_user = session.query(BotTable).filter(BotTable.chat_id == message.chat.id).first()
    if current_user is not None:
        if current_user.mode == Mode.TEXT_TO_VOICE.value:
            answer = io.BytesIO()
            audio_text = gTTS(text=message.text, lang=Lang(current_user.lang).name, slow=False)
            audio_text.write_to_fp(answer)
            answer.seek(0)
            bot.send_voice(message.chat.id, answer.read())
            # для DEBAG
            print_message(message)
        else:
            bot.send_message(message.chat.id, "Установлен другой режим")
    else:
        bot.send_message(message.chat.id, str_const.error)


@bot.message_handler(content_types=["photo"])
def repeat_text_messages(message):
    start = time.perf_counter()
    print_message(message)
    bot.send_message(message.chat.id, str_const.info_msg_photo)
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    n_clusters = 8
    if message.caption is not None and message.caption.isdigit():
        n_clusters = int(message.caption)
    photo = Photo(url=PHOTO_URL.format(TOKEN, file_info.file_path), n_clusters=n_clusters)
    bot.send_photo(
        message.chat.id,
        photo.get_result_photo(),
        caption=str_const.info_msg_photo_processing.format(time.perf_counter() - start)
    )


@bot.callback_query_handler(func=lambda call: True)
def change_settings(call):
    current_user = session.query(BotTable).filter(BotTable.chat_id == call.message.chat.id).first()
    if call.data.startswith("lang_"):
        # вызвана клавиатура для смены языка
        if call.data.endswith("ru"):
            current_user.lang = Lang.RU.value
        elif call.data.endswith("en"):
            current_user.lang = Lang.EN.value
        session.commit()
        bot.send_message(call.message.chat.id, f'Вы установили {Lang(current_user.lang).name} язык')

    elif call.data.startswith("mode_"):
        # вызвана клавиатура для смены режима
        if call.data.endswith("1"):
            current_user.mode = Mode.VOICE_TO_TEXT.value
        elif call.data.endswith("2"):
            current_user.mode = Mode.TEXT_TO_VOICE.value
        session.commit()
        bot.send_message(call.message.chat.id, f'Вы установили режим работы: {Mode(current_user.mode).name}')


if __name__ == '__main__':
    engine = create_engine(f"postgresql://{DB_config['user']}:{DB_config['password']}"
                           f"@{DB_config['host']}/{DB_config['dbname']}")
    Session = sessionmaker(bind=engine)
    session = Session()

    bot.polling(none_stop=True, interval=10)
