import requests
import datetime
import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
API_KEY_stock = '?access_key=4748196e0b1c991fde8c8bb9fe9bd7f5&format=1'
API_KEY_telegram = '1509587112:AAFRUbN-AmxgnfigSvmt_t0yskNH1mJlE_Q'
period = {'latest': 'latest'}
source = 'https://api.exchangeratesapi.io/latest?base=USD'
r = requests.get(source)
status = r.status_code


def resp(income):
    try:
        return r.json()['rates'][income]
    except KeyError:
        return 'Неверно введенный параметр'


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help yourself')


def time_difference():
    with open('request.txt', 'r', encoding='utf-8') as f:
        dt1 = datetime.datetime.strptime(f.readlines()[-1].strip(), '%H:%M:%S')
        dt2 = datetime.datetime.now()
        return (dt2 - dt1).seconds // 60


def rates_list(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /list is issued."""
    if time_difference() >= 10:
        for i in r.json()['rates']:
            update.message.reply_text(i + " : " + str(round(r.json()['rates'][i], 2)))
        save_request(r.json()['rates'])


def run_bot(update: Update, context: CallbackContext) -> None:
    response = resp(update.message.text.upper())
    update.message.reply_text(response)
    print(update.message.text)
    print(response)


def main():
    """Start the bot."""
    updater = Updater(API_KEY_telegram, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("list", rates_list))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, run_bot))
    updater.start_polling()
    updater.idle()


def save_request(currency):
    with open('request.txt', 'a', encoding='utf8') as file:
        for i in currency:
            file.write(str(i) + ':' + str(currency[i]) + '\n')
        file.write(time.strftime('%X') + '\n')


if status == 200 and __name__ == '__main__':
    main()


