import requests
import os
from requests.exceptions import HTTPError
import datetime
import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from BOT_CONFIG import API_KEY_telegram, access_key, END_POINT
from matplotlib import pyplot as plt

# Historical Rates Endpoint
options = {
    'latest': 'latest',
    'history': 'historical'
}


#  https://freecurrencyapi.net/api/v2/historical?base_currency=USD&date_from=2021-11-18&date_to=2021-11-25&apikey=10695a00-4e0e-11ec-bff2-879ea96273b0
def get_request(end_point=END_POINT, key=access_key, period=options['latest'], base_currency=None, start_date=None,
                end_date=None):
    params = {'apikey': key,
              'base_currency': base_currency,
              'date_from': start_date,
              'date_to': end_date}
    try:
        response = requests.get(end_point + period, params=params)
        response.raise_for_status()
        return response
    except HTTPError as http_err:
        print(f'HTTP Error occured: {http_err}')
        return 'Connection error. Contact your system administrator.'
    except Exception as exc:
        return f'{exc}'


def get_currency_rate(currency):
    try:
        json_data = get_request().json()
        if currency in json_data['data']:
            return str(round(json_data['data'][currency], 2))
        elif currency not in json_data['data']:
            return f'Try input valid currency code. Base currency is {json_data["query"]["base_currency"]}'
    except Exception as err:
        print(err)
        return f'Some error occured. Contact your system administrator.'


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text(f'Hello {update.effective_user.first_name}')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    # update.message.reply_text(open('README.md', 'r', encoding='utf-8').read())
    update.message.reply_text('Hello World')  # TODO handle this action


# def time_difference():
#     try:
#         with open('request.txt', 'r', encoding='utf-8') as f:
#             dt1 = datetime.datetime.strptime(f.readlines()[-1].strip(), '%H:%M:%S')
#             dt2 = datetime.datetime.now()
#             return (dt2 - dt1).seconds // 60
#     except (IndexError, FileNotFoundError):
#         return 10
#

def rates_list(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /list is issued."""
    json_data = get_request().json()
    if 'data' in json_data:
        rates = []
        for rate in sorted(json_data['data']):
            rates.append(rate + ' - ' + str(round(json_data['data'][rate], 2)))
        update.message.reply_text('\n'.join(rates))
    elif 'data' not in json_data:
        update.message.reply_text('No Information')


# end_point=END_POINT, key=access_key, period=options['latest'], base_currency='UAH', start_date=False, end_date=False
def history(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /history is issued."""
    # /history USD/EUR for 7 days
    base_currency = update.message.text.split()[1][:3].upper()
    target_currency = update.message.text.split()[1][4:7].upper()
    period_days = int(update.message.text.split()[3])  # TODO different time period, not only from today
    now_date = datetime.datetime.now()
    target_date = (now_date - datetime.timedelta(days=period_days)).strftime('%Y-%m-%d')
    response = get_request(period=options['history'],
                           base_currency=base_currency,
                           start_date=target_date,
                           end_date=now_date.strftime('%Y-%m-%d')
                           )
    dates = [i for i in response.json()['data']]
    indexes = []
    for i in dates:
        indexes.append(response.json()['data'][i][target_currency])
    file_name = 'Graph' + '-' + str(dates[0]) + '_' + str(dates[-1] + target_currency) + '.png'
    plt.plot(dates, indexes)
    plt.grid()
    plt.title(f"Rates {base_currency} to {target_currency} from {target_date} to {now_date.strftime('%Y-%m-%d')}",
              fontsize=8, loc='left')
    plt.xticks(rotation=45, fontsize=5)
    plt.yticks(fontsize=10)
    plt.ylabel('Rates')
    plt.savefig(file_name)
    plt.close()
    update.message.reply_photo(photo=open(file_name, 'rb'))
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), file_name)
    os.remove(path)


def exchange(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /exchange is issued."""
    # try:
    #     if len(update.message.text.split()) == 4:
    #         update.message.reply_text(str(round(float(
    #             update.message.text.split()[1][1:]) * float(
    #             r.json()['rates'][update.message.text.split()[3].upper()]), 2)))
    #     elif len(update.message.text.split()) == 5:
    #         update.message.reply_text(str(round(float(
    #             update.message.text.split()[1]) * float(
    #             r.json()['rates'][update.message.text.split()[-1].upper()]), 2)))
    # except KeyError:
    #     update.message.reply_text('Введены неправильные параметры.\nПовторите, пожалуйста.')


def run_bot(update: Update, context: CallbackContext) -> None:
    response = get_currency_rate(update.message.text.upper())
    try:
        update.message.reply_text(response)
    except Exception as exc:
        update.message.reply_text(exc)


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
