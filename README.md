<!DOCTYPE html>
<html>
<head>
  
</head>
<body>

<h1>Pharmacy Duty Bot</h1>

<p>This is a Telegram bot that helps users find pharmacies on duty in Germany by postal code.</p>

<h2>Features</h2>

<ul>
  <li>Enter a postal code to get pharmacies on duty for that location</li>
  <li>Automatically searches for pharmacies using the current date</li>
  <li>Returns name, address, phone number and maps link for each pharmacy</li>
  <li>Handles rate limiting and retries failed requests</li>
  <li>Requires users to join a subscription channel before access</li>
</ul>

<h2>Setup</h2>

<h3>Prerequisites</h3>

<ul>
  <li>Python 3.6+</li>
  <li><a href="https://core.telegram.org/bots#3-how-do-i-create-a-bot">Telegram bot token</a></li>
  <li><a href="https://opencagedata.com/api">OpenCage API key</a> for geocoding</li> 
</ul>

<h3>Install dependencies</h3>

<pre>
<code>
pip install -r requirements.txt
</code>  
</pre>

<h3>Configuration</h3>

<p>Add Telegram bot token, OpenCage API key and channel name to .env:</p>

<pre>
<code>
TELEGRAM_BOT_TOKEN=12345:ABC
OPENCAGE_API_KEY=6789  
CHAT_ID=@mychannel
</code>
</pre>

<h2>Usage</h2>  

<ul>
  <li>Chat with the bot or use /start</li>
  <li>Enter a postal code when prompted</li>
  <li>Bot returns pharmacies on duty near that location</li>
  <li>Tap "New search" to look up another location</li> 
</ul>

<h2>Bot Code Overview</h2>

<ul>
  <li>bot.py: Main bot logic and message handling</li>
  <li>utils.py: Helper functions for geocoding, API requests etc</li>
  <li>Logging with logging module</li>
  <li>Async polling with telebot</li>
  <li>Env vars loaded from .env with python-dotenv</li>
</ul>
  
<h2>Deployment</h2>

<p>This bot can be deployed to any service that runs Python apps e.g:</p>

<ul>
  <li><a href="https://devcenter.heroku.com/articles/getting-started-with-python">Heroku</a></li>
  <li><a href="https://help.pythonanywhere.com/pages/TelegramBots">PythonAnywhere</a></li>
  <li><a href="https://docs.microsoft.com/en-us/azure/app-service/quickstart-python">Azure App Service</a></li> 
</ul>

<h2>Resources</h2>

<ul>
  <li><a href="https://github.com/eternnoir/pyTelegramBotAPI">Telebot documentation</a></li>
  <li><a href="https://opencagedata.com/api">OpenCage Geocoding API</a></li>
  <li><a href="https://apotheken-notdienst-api.de/">Apotheken Notdienst API</a></li>
</ul>

</body>
</html>
