import os
from textwrap import dedent

import telebot
from telebot import types

from Place import Place
from Stage import Stage
from database import Database

TOKEN = os.environ.get("API_KEY")
db = Database()
memorizer = telebot.TeleBot(TOKEN)

INFO_TEXT = dedent("""
    Вас приветствует Запоминатель Мест версии 0.1!
    Используйте его для запоминания информации о местах, которые хотели бы посетить в будущем.
    Команды:
    /add - запомнить новое место
    /list - вспомнить места, в которые можно сходить
    /map - получить карту места для посещения
    /visited - отметить место как посещённое
    /reset - удалить все свои запомненные места
    /help - показать эту справку""")


@memorizer.message_handler(commands=["start", "help"])
def info(message):
    print(f"Sending help to {message.chat.id}")
    memorizer.send_message(message.chat.id, INFO_TEXT)


@memorizer.message_handler(commands=["add"])
def add(message):
    print(f"Started adding place with {message.chat.id}")
    memorizer.send_message(message.chat.id, dedent("""
    Пришлите название нового места, которое Вы хотите запомнить"""))
    db.set_user_stage(message.chat.id, Stage.ADDING_PLACE_NAME)


@memorizer.message_handler(func=lambda message:
db.get_user_stage(message.chat.id) is Stage.ADDING_PLACE_NAME)
def add_place_name(message):
    print(f"Adding place name with {message.chat.id}")
    db.set_staged_place_name(message.chat.id, message.text)
    db.set_user_stage(message.chat.id, Stage.ADDING_PLACE_LOCATION)
    memorizer.send_message(message.chat.id, dedent("""
    Теперь пришлите местоположение нового места"""))


@memorizer.message_handler(func=lambda message:
db.get_user_stage(message.chat.id) is Stage.ADDING_PLACE_LOCATION,
                           content_types=['location'])
def add_place_location(message):
    print(f"Adding place location with {message.chat.id}")
    lat, lon = message.location.latitude, message.location.longitude
    name = db.get_staged_place_name(message.chat.id)
    db.add_place(message.chat.id, Place(name, lat, lon))
    db.clean_staged_place_name(message.chat.id)
    memorizer.send_message(message.chat.id, "Новое место успешно добавлено")
    db.set_user_stage(message.chat.id, Stage.START)


@memorizer.message_handler(commands=["list"])
def list_places(message):
    print(f"Listing places for {message.chat.id}")
    places = db.get_places(message.chat.id)
    memorizer.send_message(message.chat.id, '\n'.join(place.name for place in places))


@memorizer.message_handler(commands=["reset"])
def ask_for_reset(message):
    print(f"User {message.chat.id} want to reset his places")
    db.set_user_stage(message.chat.id, Stage.ASKING_FOR_RESET)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    confirm = types.InlineKeyboardButton(text="Да, удалить", callback_data='confirm')
    abort = types.InlineKeyboardButton(text="Нет, отменить", callback_data='abort')
    keyboard.add(confirm, abort)
    memorizer.send_message(message.chat.id, "Внимание! Это действие удалит ВСЕ запомненные места "
                                            "без возможности восстановления. Желаете продолжить?",
                           reply_markup=keyboard)


@memorizer.callback_query_handler(func=lambda callback_query:
                                  db.get_user_stage(callback_query.id) is Stage.ASKING_FOR_RESET)
def confirm_request(callback_query):
    print(callback_query.message)
    print(callback_query.data)
    if callback_query.data == 'confirm':
        print(f"User {callback_query.id} successfully reset his places")
        db.reset_user(callback_query.id)
        memorizer.send_message(callback_query.id, "Вы успешно удалили всю свою информацию")
    else:
        db.set_user_stage(callback_query.id, Stage.START)
        print(f"User {callback_query.id} cancel resetting")


@memorizer.message_handler(func=lambda x: True)
def echo(message):
    print(f"Echoing to {message.chat.id}")
    memorizer.send_message(message.chat.id, f"Неизвестная команда: {message.text}. Используйте "
                                            f"/help, чтобы получить список всех команд.")


memorizer.polling(none_stop=True)
