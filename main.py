import requests
import os
from requests.exceptions import HTTPError
import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from BOT_CONFIG import API_KEY_telegram, access_key, END_POINT
from matplotlib import pyplot as plt

options = {
    'latest': 'latest',
    'history': 'historical'
}


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
        print(f'HTTP Error occurred: {http_err}')
        return 'Connection error. Contact your system administrator.'
    except Exception as exc:
        return f'{exc}'


def get_currency_rate(currency):
    if len(currency.split()) == 1:
        try:
            json_data = get_request().json()
            if currency in json_data['data']:
                return str(round(json_data['data'][currency], 2))
            elif currency not in json_data['data']:
                return f'Try input valid currency code. Base currency is {json_data["query"]["base_currency"]}'
        except Exception as err:
            print(err)
            return 'Some error occurred. Contact your system administrator.'
    elif len(currency.split()) == 2:
        base_currency, target_currency = currency.split()
        try:
            json_data = get_request(base_currency=base_currency).json()
            if target_currency in json_data['data']:
                return str(round(json_data['data'][target_currency], 2)) + target_currency
            elif currency not in json_data['data']:
                return f'Try input valid currency code. Base currency is {json_data["query"]["base_currency"]}'
        except Exception as err:
            print(err)
            return f'Try input valid currency code.'
    else:
        return """
                Valid request example: 
                'USD EUR' 
                - show rate USD to EUR to current date
                """


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""

    update.message.reply_text(f'Hello {update.effective_user.first_name}')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""

    # update.message.reply_text(open('README.md', 'r', encoding='utf-8').read())
    update.message.reply_text(
        'List of commands\n'
        '/help - list of commands\n'
        '/list - list of currencies rates to base currency(USD) on current date\n'
        '/history - history graph rates\n/exchange - change currency value\n'
        'You can also request rates one currency to another by typing, for example "USD EUR"')


def rates_list(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /list is issued."""

    json_data = get_request().json()
    if json_data and ('data' in json_data):
        rates = []
        for rate in sorted(json_data['data']):
            rates.append(rate + ' - ' + str(round(json_data['data'][rate], 2)))
        update.message.reply_text('\n'.join(rates))
    elif 'data' not in json_data:
        update.message.reply_text('No Information')


def history(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /history is issued."""

    if len(update.message.text.split()) >= 4:
        base_currency = update.message.text.split()[1][:3].upper()
        target_currency = update.message.text.split()[2].upper()
        period_days = int(update.message.text.split()[3])
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
        plt.title(f"Rates 1{base_currency} to {target_currency} from {target_date} to {now_date.strftime('%Y-%m-%d')}",
                  fontsize=8, loc='left')
        plt.xticks(rotation=45, fontsize=5)
        plt.yticks(fontsize=10)
        plt.ylabel('Rates')
        plt.savefig(file_name)
        plt.close()
        update.message.reply_photo(photo=open(file_name, 'rb'))
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), file_name)
        os.remove(path)
    else:
        update.message.reply_text("""
        Valid request example: 
        '/history USD EUR 7' 
        - show graph rate USD to EUR for last 7 days
        """)


def exchange(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /exchange is issued."""
    if len(update.message.text.split()) >= 4:
        value = int(update.message.text.split()[1])
        base_currency = update.message.text.split()[2]
        target_currency = update.message.text.split()[3]
        try:
            response = get_request(base_currency=base_currency)
            json_data = response.json()
            rate = json_data['data'][target_currency]
            result = round(value * rate, 2)
            update.message.reply_text(str(result) + target_currency)
        except KeyError:
            update.message.reply_text('There are errors in input parameters')
    else:
        update.message.reply_text("""
        Valid request example: 
        '/exchange 10 USD EUR' 
        - exchange 10 USD into EUR on current date
        """)


def run_bot(update: Update, context: CallbackContext) -> None:
    response = get_currency_rate(update.message.text.upper())
    try:
        update.message.reply_text(response)
    except Exception as exc:
        update.message.reply_text(str(exc))


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


if __name__ == '__main__':
    main()
