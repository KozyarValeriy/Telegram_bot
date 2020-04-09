import telebot
from gtts import gTTS
import os

import config

ALL_LANG = dict(ru='русский', en='английский')
ALL_MODE = {1: 'режим распозноваяния голосовый сообщений',
            2: 'режим преобразования текстовых сообщений'}
mode = 1
lang = 'ru'
PROXY_IP = '193.160.214.29'
PROXY_PORT = 3169
telebot.apihelper.proxy = {'https': f'https://{PROXY_IP}:{PROXY_PORT}'}
bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['help', 'set_lang', 'get_lang', 'set_mode', 'get_mode'])
def handle_start_help(message):
    if message.text == '/help':
        bot.send_message(message.chat.id, '''В зависимости от выбранного \
режима работы бот либо преобразует текстовые сообщения в аудио, либо аудио \
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
    режим распозноваяния голосовый сообщений''')
    elif message.text == '/set_lang':
        bot.send_message(message.chat.id, f'Текущий язык: {ALL_LANG[lang]}')
        keyboard = telebot.types.InlineKeyboardMarkup()
        key_ru = telebot.types.InlineKeyboardButton(text='Русский', callback_data='ru')
        keyboard.add(key_ru)
        key_en = telebot.types.InlineKeyboardButton(text='Английский', callback_data='en')
        keyboard.add(key_en)
        bot.send_message(message.chat.id, text='Выберите язык:', reply_markup=keyboard)
    elif message.text == '/get_lang':
        bot.send_message(message.chat.id, f'Текущий язык: {ALL_LANG[lang]}')
    elif message.text == '/set_mode':
        bot.send_message(message.chat.id, f'Текущий режим:\n\t{ALL_MODE[mode]}')
        keyboard = telebot.types.InlineKeyboardMarkup()
        key_mode_1 = telebot.types.InlineKeyboardButton(text='Голос в текст', callback_data='1')
        keyboard.add(key_mode_1)
        key_mode_2 = telebot.types.InlineKeyboardButton(text='Текст в голос', callback_data='2')
        keyboard.add(key_mode_2)
        bot.send_message(message.chat.id, text='Выбериет режим:', reply_markup=keyboard)
    elif message.text == '/get_mode':
        bot.send_message(message.chat.id, f'Текущий режим:\n\t{ALL_MODE[mode]}')


@bot.message_handler(content_types=["voice"])
def repeat_audio_messages(message):
    if mode == 1:
        bot.send_message(message.chat.id, 'Пока не работает, скоро будет') 
    print(message)


@bot.message_handler(content_types=["text"])
def repeat_text_messages(message):
    # if mode == 2:
    audio_text = gTTS(text=message.text, lang=lang, slow=False)
    # name_audio = shorten(message.text)
    name_audio = 'Audio'
    audio_text.save(f'{name_audio}.ogg')
    bot.send_voice(message.chat.id, open(f'{name_audio}.ogg', 'rb'))
    os.remove('{0}.ogg'.format(name_audio))
    print(message)


@bot.callback_query_handler(func=lambda call: True)
def change_language(call):
    global lang
    if call.data == "ru":
        lang = 'ru'
    elif call.data == "en":
        lang = 'en'
    bot.send_message(call.message.chat.id, f'Вы установили {ALL_LANG[lang]} язык')


@bot.callback_query_handler(func=lambda call: True)
def change_mode(call):
    global mode
    if call.data == '1':
        mode = 1
    elif call.data == '2':
        mode = 2
    bot.send_message(call.message.chat.id, f'Текущий режим работы:\n\t{ALL_MODE[mode]}')


def shorten(text, length=10, indicator='... '):
    if len(text) > length:
        text = text[:(length - len(indicator))] + indicator
    return text


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
