import os

import telebot

TOKEN = os.environ.get("API_KEY")
memorizer = telebot.TeleBot(TOKEN)


@memorizer.message_handler()
def echo(message):
    print("Reply to %s" % message.chat.id)
    memorizer.reply_to(message, message.text)


memorizer.polling(none_stop=True)
