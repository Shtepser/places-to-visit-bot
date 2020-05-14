import os
from textwrap import dedent

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

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
    /list - вспомнить места, в которые можно отправиться
    /random - выбрать случайное место из запомненных и получить его карту
    /visited - отметить место как посещённое
    /reset - удалить все свои запомненные места
    /help - показать эту справку""")


def is_asking_for_reset(user_id):
    return db.get_user_stage(user_id) is Stage.ASKING_FOR_RESET


def is_adding_place_name(user_id):
    return db.get_user_stage(user_id) is Stage.ADDING_PLACE_NAME


def is_adding_place_location(user_id):
    return db.get_user_stage(user_id) is Stage.ADDING_PLACE_LOCATION


def create_places_keyboard(places, page=0):
    keyboard = InlineKeyboardMarkup(row_width=1)
    if page != 0:
        keyboard.add(InlineKeyboardButton(text="Предыдущие места",
                                          callback_data=f'to_page_{page - 1}'))
    keyboard.add(*[InlineKeyboardButton(text=place.name, callback_data=place.name)
                   for place in places[page * 10:(page + 1) * 10]])
    if len(places) >= (page + 1) * 10:
        keyboard.add(InlineKeyboardButton(text="Следующие места",
                                          callback_data=f'to_page_{page + 1}'))
    return keyboard


@memorizer.callback_query_handler(func=lambda query: is_asking_for_reset(query.message.chat.id))
def confirm_request(callback_query):
    if callback_query.data == 'confirm':
        db.reset_user(callback_query.message.chat.id)
        memorizer.answer_callback_query(callback_query.id, "Вы успешно удалили всю свою информацию")
        print(f"User {callback_query.message.chat.id} successfully reset his places")
    else:
        db.set_user_stage(callback_query.message.chat.id, Stage.START)
        memorizer.answer_callback_query(callback_query.id, "Вы отменили удаление информации")
        print(f"User {callback_query.message.chat.id} cancel resetting")


@memorizer.callback_query_handler(func=lambda query: query.data.startswith("to_page_"))
def show_places_page(callback_query):
    target_page = int(callback_query.data.lstrip("to_page_"))
    if target_page:
        places = db.get_places(callback_query.message.chat.id)
        memorizer.send_message(callback_query.message.chat.id, "Ваши запомненные места",
                               reply_markup=create_places_keyboard(places, target_page))


@memorizer.callback_query_handler(func=lambda x: True)
def show_map_for_place(callback_query):
    user_id = callback_query.message.chat.id
    place = db.get_place_by_name(user_id, callback_query.data)
    memorizer.send_message(user_id, f"Карта для {place.name}")
    memorizer.send_location(user_id, place.lat, place.lon)


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


@memorizer.message_handler(func=lambda message: is_adding_place_name(message.chat.id))
def add_place_name(message):
    print(f"Adding place name with {message.chat.id}")
    db.set_staged_place_name(message.chat.id, message.text)
    db.set_user_stage(message.chat.id, Stage.ADDING_PLACE_LOCATION)
    memorizer.send_message(message.chat.id, dedent("""
    Теперь пришлите местоположение нового места"""))


@memorizer.message_handler(func=lambda message: is_adding_place_location(message.chat.id),
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
    if places:
        memorizer.send_message(message.chat.id, "Ваши запомненные места",
                               reply_markup=create_places_keyboard(places))
    else:
        memorizer.send_message(message.chat.id, "Вы ещё не запомнили никаких мест")


@memorizer.message_handler(commands=["visited"])
def visited(message):
    pass


@memorizer.message_handler(commands=["reset"])
def ask_for_reset(message):
    print(f"User {message.chat.id} want to reset his places")
    db.set_user_stage(message.chat.id, Stage.ASKING_FOR_RESET)
    keyboard = InlineKeyboardMarkup(row_width=2)
    confirm = InlineKeyboardButton(text="Да, удалить", callback_data='confirm')
    abort = InlineKeyboardButton(text="Нет, отменить", callback_data='abort')
    keyboard.add(confirm, abort)
    memorizer.send_message(message.chat.id, "Внимание! Это действие удалит ВСЕ запомненные места "
                                            "без возможности восстановления. Желаете продолжить?",
                           reply_markup=keyboard)


@memorizer.message_handler(func=lambda x: True)
def echo(message):
    print(f"Echoing to {message.chat.id}")
    memorizer.send_message(message.chat.id, f"Неизвестная команда: {message.text}. Используйте "
                                            f"/help, чтобы получить список всех команд.")


memorizer.polling(none_stop=True)
