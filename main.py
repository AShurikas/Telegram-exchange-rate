import requests
import datetime
import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from BOT_CONFIG import API_KEY_telegram
from matplotlib import pyplot as plt

period = {'latest': 'latest'}
source = 'https://api.exchangeratesapi.io/latest?base=USD'
source_for_history = 'https://api.exchangeratesapi.io/history?'
r = requests.get(source)
status = r.status_code


def resp(income):
    try:
        return r.json()['rates'][income]
    except KeyError:
        return 'Неверно введенный параметр'


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! Type /help to see commands')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(open('README.md', 'r', encoding='utf-8').read())


def time_difference():
    try:
        with open('request.txt', 'r', encoding='utf-8') as f:
            dt1 = datetime.datetime.strptime(f.readlines()[-1].strip(), '%H:%M:%S')
            dt2 = datetime.datetime.now()
            return (dt2 - dt1).seconds // 60
    except (IndexError, FileNotFoundError):
        return 10


def rates_list(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /list is issued."""
    if time_difference() >= 10:
        for i in r.json()['rates']:
            update.message.reply_text(i + " : " + str(round(r.json()['rates'][i], 2)))
        save_request(r.json()['rates'])
    else:
        for i in open('request.txt', 'r', encoding='utf-8').readlines()[:-1]:
            update.message.reply_text(i[:4] + str(round(float(i[4:]), 2)))


def history(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /history is issued."""
    period_days = int(update.message.text.split()[3])
    rate_index = update.message.text.split()[1][4:7].upper()
    now_date = datetime.datetime.now()
    target_date = (now_date - datetime.timedelta(days=period_days)).strftime('%Y-%m-%d')
    req = requests.get(source_for_history
                       + 'start_at=' + target_date
                       + '&end_at=' + now_date.strftime('%Y-%m-%d')
                       + '&base=USD&symbols=' + rate_index)
    dates = [i for i in req.json()['rates']]
    indexes = []
    for i in dates:
        indexes.append(req.json()['rates'][i][rate_index])
    file_name = 'Graph' + '-' + str(dates[0]) + '_' + str(dates[-1] + rate_index) + '.png'
    plt.plot(sorted(dates), sorted(indexes))
    plt.xlabel('Dates')
    plt.ylabel('Rates')
    plt.savefig(file_name)
    plt.close()
    update.message.reply_photo(photo=open(file_name, 'rb'))
    

def exchange(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /exchange is issued."""
    try:
        if len(update.message.text.split()) == 4:
            update.message.reply_text(str(round(float(
                update.message.text.split()[1][1:]) * float(
                r.json()['rates'][update.message.text.split()[3].upper()]), 2)))
        elif len(update.message.text.split()) == 5:
            update.message.reply_text(str(round(float(
                update.message.text.split()[1]) * float(
                r.json()['rates'][update.message.text.split()[-1].upper()]), 2)))
    except KeyError:
        update.message.reply_text('Введены неправильные параметры.\nПовторите, пожалуйста.')


def run_bot(update: Update, context: CallbackContext) -> None:
    response = resp(update.message.text.upper())
    update.message.reply_text(response)


def main():
    """Start the bot."""
    updater = Updater(API_KEY_telegram, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("list", rates_list))
    dispatcher.add_handler(CommandHandler("exchange", exchange))
    dispatcher.add_handler(CommandHandler("history", history))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, run_bot))
    updater.start_polling()
    updater.idle()


def save_request(currency):
    with open('request.txt', 'w', encoding='utf8') as file:
        for i in currency:
            file.write(str(i) + ':' + str(currency[i]) + '\n')
        file.write(time.strftime('%X') + '\n')


if __name__ == '__main__':
    main()
