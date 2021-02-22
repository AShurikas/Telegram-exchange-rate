import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

API_KEY_stock = '?access_key=4748196e0b1c991fde8c8bb9fe9bd7f5&format=1'
period = {'latest': 'latest'}
source = 'http://data.fixer.io/api/'
r = requests.get(source+period['latest']+API_KEY_stock)
status = r.status_code


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! I will help you to know exchange rates on stock market')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def run_bot(update: Update, context: CallbackContext) -> None:
    response = r.json()['rates'][update.message.text.upper()]
    update.message.reply_text(response)
    print(update.message.text)
    print(response)


def main():
    """Start the bot."""
    updater = Updater("1509587112:AAFRUbN-AmxgnfigSvmt_t0yskNH1mJlE_Q", use_context=True)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, run_bot))

    updater.start_polling()
    updater.idle()


if status == 200:
    main()






