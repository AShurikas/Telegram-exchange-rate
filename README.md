Exchange-rate-bot-Telegram
==========================
To start you have to configure your own 'API_KEY_telegram' for the bot. Once the currency data is loaded from the web service, it saves into the local storage 'requests.txt'. Next time currency data will be downloaded from web service after 10 minutes. Otherwise - data will be downloaded from previous set in the local storage. Default currency is USD.

---

_Commands:_

**'currency code'****(example: eur)** - returns exchange rate selected currency to USD;

**/list** - returns list of rates USD to other currencies;

**/exchange $10 to 'currency code'** or 
**/exchange 10 USD to 'currency code'** - converts to the second currency with two
decimal precision;

**/history USD/'currency code' for 7 days** **(example: /history USD/EUR for 7 days)** - return an image graph chart which shows the exchange rate of the selected currency to USD for the last 7 days.

