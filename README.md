# Telegram-exchange-rate
           Exchange rate bot Telegram
Commands: 

/list - returns currency data;

'currency code' - returns exchange rate selected currency to USD;

/exchange $10 to CAD or 
/exchange 10 USD to CAD - converts to the second currency with two
decimal precision and return.


To start you have to configure your own 'API_KEY_telegram' for the bot.
Once the currency data is loaded from the web service, it saves into the local storage 'requests.txt'.
Next time currency data will be downloaded from web service after 10 minutes.
Otherwise - data will be downloaded from previous set in the local storage.
