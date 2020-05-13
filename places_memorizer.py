import os

import telebot

TOKEN = os.environ.get("API_KEY")
memorizer = telebot.TeleBot(TOKEN)


@memorizer.message_handler(commands=["/start", "/help"])
def info(message):
    print(f"Replying to {message.chat.id}")
    memorizer.reply_to(message, """
    Вас приветствует Запоминатель Мест версии 0.1!
    Используйте его для запоминания информации о местах, которые хотели бы посетить в будущем.
    Команды:
    /add - запомнить новое место
    /list - вспомнить места, в которые можно сходить
    /map - получить карту места для посещения
    /visited - отметить место как посещённое
    /reset - удалить все свои запомненные места
    /help - показать эту справку""")


memorizer.polling(none_stop=True)
