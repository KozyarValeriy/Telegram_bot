import telebot
from gtts import gTTS
import pprint
import json

import config
from save_answer_voice import Sound
import answer_constants_rus
from database import SingletonDB

# константы
LANG = {1: "ru", 2: "en"}
LANG_FOR_USER = {1: 'русский', 2: 'английский'}
ALL_MODE = {1: 'режим распозноваяния голосовый сообщений',
            2: 'режим преобразования текстовых сообщений'}

# подключение к БД
DB = SingletonDB(config.DB_config)

telebot.apihelper.proxy = {'http': f'socks5://{config.PROXY_IP}:{config.PROXY_PORT}',
                           'https': f'socks5://{config.PROXY_IP}:{config.PROXY_PORT}'}
bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['help', 'start', 'set_lang', 'get_lang', 'set_mode', 'get_mode'])
def handle_start_help(message):
    try:
        if message.text == '/help':
            bot.send_message(message.chat.id, answer_constants_rus.help_message)
        elif message.text == '/start':
            # отправляем приветсвенное сообщение
            bot.send_message(message.chat.id, answer_constants_rus.hello_message)
            # добавление в базу нового чата
            DB.add_new_user(message.chat.id, 2, 1)

        elif message.text == '/set_lang':
            current_chat = DB.get_user(message.chat.id)
            bot.send_message(message.chat.id, f'Текущий язык: {LANG_FOR_USER[current_chat["lang"]]}')

            # Добавление клавиатуры для выбора языка
            keyboard = telebot.types.InlineKeyboardMarkup()
            key_ru = telebot.types.InlineKeyboardButton(text='Русский', callback_data='lang_ru')
            keyboard.add(key_ru)
            key_en = telebot.types.InlineKeyboardButton(text='Английский', callback_data='lang_en')
            keyboard.add(key_en)
            bot.send_message(message.chat.id, text='Выберите язык:', reply_markup=keyboard)

        elif message.text == '/get_lang':
            current_chat = DB.get_user(message.chat.id)
            bot.send_message(message.chat.id, f'Текущий язык: {LANG_FOR_USER[current_chat["lang"]]}')

        elif message.text == '/set_mode':
            current_chat = DB.get_user(message.chat.id)
            bot.send_message(message.chat.id, f'Текущий режим:\n\t{ALL_MODE[current_chat["mode"]]}')

            # Добавление клавиатуры для выбора языка
            keyboard = telebot.types.InlineKeyboardMarkup()
            key_mode_1 = telebot.types.InlineKeyboardButton(text='Голос в текст', callback_data='mode_1')
            keyboard.add(key_mode_1)
            key_mode_2 = telebot.types.InlineKeyboardButton(text='Текст в голос', callback_data='mode_2')
            keyboard.add(key_mode_2)
            bot.send_message(message.chat.id, text='Выбериет режим:', reply_markup=keyboard)

        elif message.text == '/get_mode':
            current_chat = DB.get_user(message.chat.id)
            bot.send_message(message.chat.id, f'Текущий режим: {ALL_MODE[current_chat["mode"]]}')

    except KeyError:
        # При этой ошибке сокрее всего пользователь еще не в базе. Добавляем
        DB.add_new_user(message.chat.id, 2, 1)


@bot.message_handler(content_types=["voice"])
def repeat_audio_messages(message):
    current_chat = DB.get_user(message.chat.id)
    if current_chat["mode"] == 1:
        bot.send_message(message.chat.id, 'Пока не работает, скоро будет') 
    print(message)


@bot.message_handler(content_types=["text"])
def repeat_text_messages(message):
    current_chat = DB.get_user(message.chat.id)
    if current_chat is not None:
        if current_chat["mode"] == 2:
            answer = Sound()
            audio_text = gTTS(text=message.text, lang=LANG[current_chat["lang"]], slow=False)
            audio_text.write_to_fp(answer)
            bot.send_voice(message.chat.id, answer.get_data())

            # для DEBAG
            pprint.pprint(json.loads(str(message).replace("'", '"').replace('False', '"False"')
                                                 .replace('True', '"True"').replace('None', '"None"')))
            print(message.text)
        else:
            print('Установлен другой режим')
    else:
        DB.add_new_user(message.chat.id, 2, 1)


@bot.callback_query_handler(func=lambda call: True)
def change_settings(call):
    if call.data.startswith("lang_"):
        # вызвана клавиатура для смены языка
        if call.data.endswith("ru"):
            DB.update(call.message.chat.id, "lang", 1)
        elif call.data.endswith("en"):
            DB.update(call.message.chat.id, "lang", 2)
        current_chat = DB.get_user(call.message.chat.id)
        bot.send_message(call.message.chat.id, f'Вы установили {LANG_FOR_USER[current_chat["lang"]]} язык')

    elif call.data.startswith("mode_"):
        # вызвана клавиатура для смены режима
        if call.data.endswith("1"):
            DB.update(call.message.chat.id, "mode", 1)
        elif call.data.endswith("2"):
            DB.update(call.message.chat.id, "mode", 2)
        current_chat = DB.get_user(call.message.chat.id)
        bot.send_message(call.message.chat.id, f'Вы установили режим работы:\n\t{ALL_MODE[current_chat["mode"]]}')


if __name__ == '__main__':
    try:
        # conf = configparser.ConfigParser()
        # conf.read('config.ini')
        bot.polling(none_stop=True, interval=10)
    finally:
        DB.close()
