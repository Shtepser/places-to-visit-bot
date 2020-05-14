import os
from random import choice
from textwrap import dedent

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from Place import Place
from Stage import Stage
from database import Database

TOKEN = os.environ.get("API_KEY")
db = Database()
memorizer = telebot.TeleBot(TOKEN)

PLACES_PER_PAGE = 5

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


def is_searching_place_to_visit(user_id):
    return db.get_user_stage(user_id) is Stage.SEARCHING_PLACE_TO_VISIT


def is_marking_place_as_visited(user_id):
    return db.get_user_stage(user_id) is Stage.MARKING_PLACE_AS_VISITED


def places_keyboard(places, page=0):
    keyboard = InlineKeyboardMarkup(row_width=1)
    if page != 0:
        keyboard.add(InlineKeyboardButton(text="Предыдущие места",
                                          callback_data=f'to_page_{page - 1}'))
    keyboard.add(*[InlineKeyboardButton(text=place.name, callback_data=place.name)
                   for place in places[page * PLACES_PER_PAGE:(page + 1) * PLACES_PER_PAGE]])
    if len(places) > (page + 1) * PLACES_PER_PAGE:
        keyboard.add(InlineKeyboardButton(text="Следующие места",
                                          callback_data=f'to_page_{page + 1}'))
    return keyboard


def send_places_list(user_id):
    places = db.get_places(user_id)
    if places:
        memorizer.send_message(user_id, "Ваши запомненные места",
                               reply_markup=places_keyboard(places))
    else:
        memorizer.send_message(user_id, "Вы ещё не запомнили никаких мест")


def send_place_info(user_id, place):
    memorizer.send_message(user_id, f"Карта для {place.name}")
    memorizer.send_location(user_id, place.lat, place.lon)


@memorizer.callback_query_handler(func=lambda query: is_asking_for_reset(query.message.chat.id))
def confirm_reset(callback_query):
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
    places = db.get_places(callback_query.message.chat.id)
    memorizer.answer_callback_query(callback_query.id)
    memorizer.send_message(callback_query.message.chat.id, "Ваши запомненные места",
                           reply_markup=places_keyboard(places, target_page))


@memorizer.callback_query_handler(func=lambda query:
                                  is_searching_place_to_visit(query.message.chat.id))
def show_map_for_place(callback_query):
    user_id = callback_query.message.chat.id
    place = db.get_place_by_name(user_id, callback_query.data)
    send_place_info(user_id, place)
    memorizer.answer_callback_query(callback_query.id, f"Чтобы показать другие места, "
                                                       f"начните новый поиск командой /list")
    db.set_user_stage(user_id, Stage.START)


@memorizer.callback_query_handler(func=lambda query:
                                  is_marking_place_as_visited(query.message.chat.id))
def mark_place_as_visited(callback_query):
    user_id = callback_query.message.chat.id
    place = db.get_place_by_name(user_id, callback_query.data)
    memorizer.answer_callback_query(callback_query.id, f"Вы посетили {place.name}."
                                                       f"Чтобы посетить ещё одно место, "
                                                       f"начните новый поиск командой /visited")
    db.remove_place(user_id, place)
    db.set_user_stage(user_id, Stage.START)


@memorizer.message_handler(commands=["start"])
def start(message):
    if db.has_user(message.chat.id):
        print(f"Starting with user {message.chat.id}")
        memorizer.send_message(message.chat.id, "С возвращением!")
    else:
        print(f"New user: {message.chat.id}")
        memorizer.send_message(message.chat.id, "Добро пожаловать!\n" + INFO_TEXT)
    db.set_user_stage(message.chat.id, Stage.START)


@memorizer.message_handler(commands=["help"])
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
    db.set_user_stage(message.chat.id, Stage.SEARCHING_PLACE_TO_VISIT)
    send_places_list(message.chat.id)


@memorizer.message_handler(commands=["visited"])
def visited(message):
    print(f"Marking place as visited for {message.chat.id}")
    db.set_user_stage(message.chat.id, Stage.MARKING_PLACE_AS_VISITED)
    send_places_list(message.chat.id)


@memorizer.message_handler(commands=["random"])
def send_random_place(message):
    print(f"Sending random place to {message.chat.id}")
    place = choice(db.get_places(message.chat.id))
    send_place_info(message.chat.id, place)


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
