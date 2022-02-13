import asyncio
import io
import os
import queue
import time

import telebot
from telebot.async_telebot import AsyncTeleBot
from gtts import gTTS

from logger import get_logger
from models import BotTable, Lang
from models.db import async_session
from photo import PhotoWorker
from string_constant import rus as str_const


# constants
TOKEN = os.getenv("TOKEN")
PHOTO_URL = "https://api.telegram.org/file/bot{0}/{1}"
LOADING = {"\\": "|", "|": "/", "/": "-", "-": "\\"}


bot = AsyncTeleBot(TOKEN)
log = get_logger(__name__)


@bot.message_handler(commands=['help'])
async def handle_help(message: telebot.types.Message):
    """ Handle for processing message /help """
    log.info("Handling /help")
    log.debug(str(message))
    await bot.send_message(message.chat.id, str_const.help_message)


@bot.message_handler(commands=['start'])
async def handle_start(message: telebot.types.Message):
    """ Handle for processing message /start """
    log.info("Handling /start")
    log.debug(str(message))
    try:
        async with async_session() as session:
            current_user = await BotTable.get_chat_async(message.chat.id, session)
        # adding new user if not exist
        if current_user is None:
            user = BotTable(chat_id=message.chat.id, lang=Lang.RU.value)
            async with async_session() as session:
                session.add(user)
                await session.commit()
            # sending hello message
            await bot.send_message(message.chat.id, str_const.hello_message)
        else:
            await bot.send_message(message.chat.id, str_const.user_exists)

    except Exception as err:
        log.error(f"Some error occurred: {err}")
        await bot.send_message(message.chat.id, str_const.error.format(err=str(err)))


@bot.message_handler(commands=['stop'])
async def handle_stop(message: telebot.types.Message):
    """ Handle for processing message /stop """
    log.info("Handling /stop")
    log.debug(str(message))
    try:
        async with async_session() as session:
            current_user = await BotTable.get_chat_async(message.chat.id, session)
        # deleting user if exist
        if current_user is None:
            async with async_session() as session:
                session.delete(current_user)
                await session.commit()
            # sending hello message
            await bot.send_message(message.chat.id, str_const.farewell_msg)
        else:
            await bot.send_message(message.chat.id, str_const.unauthorized)
    except Exception as err:
        log.error(f"Some error occurred: {err}")
        await bot.send_message(message.chat.id, str_const.error.format(err=str(err)))


@bot.message_handler(commands=['set_lang', 'get_lang'])
async def handle_lang(message: telebot.types.Message):
    """ Handle for processing message /set_lang, /get_lang """
    log.info("Handling /set_lang, /get_lang")
    log.debug(str(message))
    try:
        async with async_session() as session:
            current_user = await BotTable.get_chat_async(message.chat.id, session)
        if current_user is None:
            await bot.send_message(message.chat.id, str_const.unauthorized)
            return
        if message.text == '/set_lang':
            # adding keyboard for lang choosing
            keyboard = telebot.types.InlineKeyboardMarkup()
            key_ru = telebot.types.InlineKeyboardButton(text=str_const.rus, callback_data='lang_ru')
            key_en = telebot.types.InlineKeyboardButton(text=str_const.eng, callback_data='lang_en')
            keyboard.add(key_ru, key_en)
            await bot.send_message(message.chat.id, text=str_const.change_lang, reply_markup=keyboard)
        else:
            await bot.send_message(message.chat.id, str_const.current_lang.format(Lang(current_user.lang).name))
    except Exception as err:
        log.error(f"Some error occurred: {err}")
        await bot.send_message(message.chat.id, str_const.error.format(err=str(err)))


@bot.message_handler(content_types=["voice"])
async def repeat_audio_messages(message: telebot.types.Message):
    """ Handle for processing voice message """
    log.info("Handling voice")
    log.debug(str(message))
    async with async_session() as session:
        current_user = await BotTable.get_chat_async(message.chat.id, session)
    if current_user is None:
        await bot.send_message(message.chat.id, str_const.unauthorized)
    await bot.send_message(message.chat.id, str_const.not_work)


@bot.message_handler(content_types=["text"])
async def text_messages(message: telebot.types.Message):
    """ Handle for processing text message """
    log.info("Handling text")
    log.debug(str(message))
    try:
        async with async_session() as session:
            current_user = await BotTable.get_chat_async(message.chat.id, session)
        if current_user is None:
            await bot.send_message(message.chat.id, str_const.unauthorized)
            return
        answer = io.BytesIO()
        audio_text = gTTS(text=message.text, lang=Lang(current_user.lang).name.lower(), slow=False)
        audio_text.write_to_fp(answer)
        answer.seek(0)
        await bot.send_voice(message.chat.id, answer.read())
    except Exception as err:
        log.error(f"Some error occurred: {err}")
        await bot.send_message(message.chat.id, str_const.error.format(err=str(err)))


@bot.message_handler(content_types=["photo"])
async def photo_messages(message: telebot.types.Message):
    """ Handle for processing image in message """
    log.info("Handling photo")
    log.debug(str(message))
    try:
        async with async_session() as session:
            current_user = await BotTable.get_chat_async(message.chat.id, session)
        if current_user is None:
            await bot.send_message(message.chat.id, str_const.unauthorized)
            return
        start = time.perf_counter()
        await bot.send_message(message.chat.id, str_const.info_msg_photo)
        file_id = message.photo[-1].file_id
        file_info = await bot.get_file(file_id)
        n_clusters = 3
        if message.caption is not None and message.caption.isdigit():
            n_clusters = int(message.caption)

        photo = PhotoWorker(url=PHOTO_URL.format(TOKEN, file_info.file_path), n_clusters=n_clusters)
        photo.start()

        current_loading_char = "\\"
        msg = await bot.send_message(
            message.chat.id,
            str_const.image_processing.format(loading=current_loading_char, time=time.perf_counter()-start)
        )
        while True:
            try:
                await asyncio.sleep(0.5)
                result = photo.queue.get_nowait()
                break
            except queue.Empty:
                current_loading_char = LOADING[current_loading_char]
                await bot.edit_message_text(
                    str_const.image_processing.format(loading=current_loading_char,
                                                      time=time.perf_counter()-start),
                    message.chat.id, msg.id
                )
        photo.join(timeout=1)
        await bot.delete_message(message.chat.id, msg.id)
        await bot.send_photo(
            message.chat.id,
            result,
            caption=str_const.info_msg_photo_processing.format(time.perf_counter()-start)
        )
        print("end photo")
    except Exception as err:
        log.error(f"Some error occurred: {err}")
        await bot.send_message(message.chat.id, str_const.error.format(err=str(err)))


@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
async def change_settings(call):
    """ Function for showing keyboard """
    log.info("Handling keyboard for lang_")
    async with async_session() as session:
        current_user = await BotTable.get_chat_async(call.message.chat.id, session)
    if current_user is None:
        await bot.send_message(call.message.chat.id, str_const.unauthorized)
        return
    if call.data.endswith("ru"):
        current_user.lang = Lang.RU.value
    elif call.data.endswith("en"):
        current_user.lang = Lang.EN.value
    async with async_session() as session:
        session.add(current_user)
        await session.commit()
    await bot.send_message(call.message.chat.id, str_const.changed_lang.format(lang=Lang(current_user.lang).name))


if __name__ == '__main__':
    log.info("Starting bot")
    asyncio.run(bot.infinity_polling())
