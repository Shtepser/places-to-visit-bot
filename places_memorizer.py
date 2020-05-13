import os

import telebot


TOKEN = os.environ.get("API_KEY")
memorizer = telebot.TeleBot(TOKEN)
print(TOKEN)
memorizer.polling(none_stop=True)


@memorizer.message_handler()
def echo(message):
    memorizer.reply_to(message, message.text)
