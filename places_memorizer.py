import os
from textwrap import dedent

import telebot

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
    memorizer.send_message(message.chat.id,  dedent("""
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


@memorizer.message_handler(func=lambda x: True)
def echo(message):
    print(f"Echoing to {message.chat.id}")
    memorizer.send_message(message.chat.id, f"Неизвестная команда: {message.text}. Используйте "
                                            f"/help, чтобы получить список всех команд.")


memorizer.polling(none_stop=True)
