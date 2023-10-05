import os
import logging
import telebot
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from telebot import types

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Global variables
CHAT_ID = "@Yourchannel"
NOTSUB_MESSAGE = "Для доступа к нашему боту, подпишитесь на наш чат @Yourchannel"

# Initialize bot
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))

# API key for OpenCage Geocoder
OPENCAGE_API_KEY = os.getenv('OPENCAGE_API_KEY')

# Safe polling function
def safe_polling():
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except telebot.apihelper.ApiTelegramException as e:
            if e.error_code == 429:  # Too Many Requests
                sleep_time = e.result_json['parameters']['retry_after']
                logger.warning(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
                time.sleep(sleep_time)
                continue
            else:
                raise e
        except Exception as e:
            logger.error(f"Unknown error occurred: {e}")
            time.sleep(15)

# Make API calls with retry
def make_request_with_retry(api_call_func, *args, **kwargs):
    max_retries = 5
    retry_delay = 5  # Delay time in seconds
    retries = 0
    
    while retries < max_retries:
        try:
            return api_call_func(*args, **kwargs)
        except Exception as e:
            if "429" in str(e):
                logger.warning(f"API call rate-limited, retrying in {retry_delay} seconds. Retries: {retries}/{max_retries}")
                time.sleep(retry_delay)
                retries += 1
            else:
                logger.error(f"API call failed due to {e}")
                raise

# Function to check if the user is subscribed to the channel
def check_sub_channel(user_id):
    try:
        chat_member = make_request_with_retry(bot.get_chat_member, CHAT_ID, user_id)
        return chat_member.status not in ['left', 'kicked']
    except Exception as e:
        logger.error(f"An error occurred while checking channel subscription: {e}")
        return False

# Callback for starting a new search
@bot.callback_query_handler(func=lambda call: call.data == 'start_new_search')
def start_new_search(call):
    bot.send_message(call.message.chat.id, "Введите индекс города, чтобы начать новый поиск.")

# Handler for /start command
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'private':  # Check for private chat
        user_id = message.from_user.id
        if check_sub_channel(user_id):
            bot.send_message(
                message.chat.id,
                f"Привет, {message.from_user.first_name}, Круто, что ты с нами! Введите индекс города, чтобы начать."
            )
        else:
            bot.send_message(message.chat.id, NOTSUB_MESSAGE)

# Main handler for text messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.chat.type == 'private':  # Check for private chat
        chat_id = message.chat.id
        location = message.text.strip()
        if location.isnumeric():  # Check if the text is likely a postal code
            date = datetime.now()  # Automatically use the current date
            coordinates = get_coordinates(location)
            if coordinates:
                pharmacies = get_pharmacies(coordinates, date)
                response = format_pharmacies(pharmacies)
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Начать новый поиск", callback_data='start_new_search'))
                bot.send_message(chat_id, response, reply_markup=markup)
            else:
                bot.send_message(chat_id, "Не удалось получить координаты для указанного индекса.")
        else:
            bot.send_message(chat_id, "Пожалуйста, введите корректный индекс города.")

# Function to get coordinates based on postal code
def get_coordinates(location):
    try:
        url = f"https://api.opencagedata.com/geocode/v1/json?key={OPENCAGE_API_KEY}&q={location}&countrycode=de"
        response = make_request_with_retry(requests.get, url)
        response.raise_for_status()
        data = response.json()
        if data["results"]:
            lat = data["results"][0]["geometry"]["lat"]
            lon = data["results"][0]["geometry"]["lng"]
            return lat, lon
    except requests.RequestException as e:
        logger.error(f"Failed to get coordinates: {e}")
    except KeyError as e:
        logger.error(f"Key error while parsing coordinates: {e}")
    return None

# Function to get a list of pharmacies based on coordinates and date
def get_pharmacies(coordinates, date):
    try:
        lat, lon = coordinates
        timestamp = int(date.timestamp() * 1000)
        url = f"https://apotheken-notdienst-api.netlify.app/.netlify/functions/server?lat={lat}&lon={lon}&date={timestamp}"
        response = make_request_with_retry(requests.get, url)
        response.raise_for_status()
        pharmacies = response.json()
        return pharmacies
    except requests.RequestException as e:
        logger.error(f"Failed to get pharmacies: {e}")
    except KeyError as e:
        logger.error(f"Key error while parsing pharmacies: {e}")
    return None

# Function to format the list of pharmacies
def format_pharmacies(pharmacies):
    if pharmacies:
        formatted = "Дежурные аптеки:/Pharmacies on duty:\n\n"
        for pharmacy in pharmacies:
            formatted += f"Название/ Title: {pharmacy['name']}\n"
            formatted += f"Адрес:/ Address: {pharmacy['street']}, {pharmacy['zip']} {pharmacy['city']}\n"
            formatted += f"Телефон/ phone number: {pharmacy['phone']}\n"
            formatted += f"Время обслуживания/ Service time: {pharmacy['serviceTime']}\n"
            address = f"{pharmacy['street']}, {pharmacy['zip']} {pharmacy['city']}"
            formatted += f"Google Maps: https://www.google.com/maps/search/?api=1&query={address.replace(' ', '+')}\n\n"
        return formatted
    else:
        return "Информация о дежурных аптеках не найдена./Information about pharmacies on duty was not found."

# Start the bot
safe_polling()
