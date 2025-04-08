from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext)
from ChatGPT_HKBU import HKBU_ChatGPT 
import logging
import redis
import os
import requests
import time

## weather function library ##
from datetime import datetime, timedelta
from collections import Counter
## check stock price with the yFinance##
import yfinance as yf
<<<<<<< HEAD

=======
>>>>>>> 8e55542 (20250408 version K)


def main():
    updater = Updater(token=(os.environ['TELEGRAM_ACCESS_TOKEN']), use_context=True) #- used for fly.io/Azure
    dispatcher = updater.dispatcher
    """Basic connection example."""

    import redis
    r = redis.Redis(
        host='redis-12417.crce178.ap-east-1-1.ec2.redns.redis-cloud.com',
        port=12417,
        decode_responses=True,
        username="default",
        password = os.environ['REDIS_ACCESS_TOKEN'] 
    )

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    # register a dispatcher to handle message: here we register an echo dispatcher
    # dispatcher for chatgpt
    global chatgpt
    chatgpt = HKBU_ChatGPT()
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command),equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)
    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("weather", weather))
    dispatcher.add_handler(CommandHandler("forecast", forecast))
    dispatcher.add_handler(CommandHandler("stock", stock))
    dispatcher.add_handler(CommandHandler("profile", profile))
    dispatcher.add_handler(CommandHandler("match", match))
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt))
    # To start the bot:
    updater.start_polling()
    updater.idle()

<<<<<<< HEAD
#def echo(update, context):
    #if update.message.text == 'What is your name?':
        #reply_message = 'I am DonaldC-Bot.'
        #context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)
    #else:
        #reply_message = update.message.text.upper()
        #logging.info("Update: " + str(update))
        #logging.info("context: " + str(context))
        #context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update:" +str(update))
    logging.info("context:" + str(context))
    context.bot.send_message(chat_id = update.effective_chat.id, text=reply_message)

=======
def hello(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /hello is issued."""
    msg = context.args[0]
    update.message.reply_text('Good day,'+ msg +'!')

# /help: provide the chatbot's available information
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Welcome to the Chatbot created by Donald, Ken and Gary! \n You may use the function below for specific features embeded in this chatbot. By default, all answers will be answered by the ChatGPT if no special function is called. \n 1. /help: Display this help message. \n 2. /add <text> : Type your name and register in the database. \n 3. /weather <location> : Display the weather by location. The weather of Hong Kong will be shown if no location is specified. \n 4. forcast <location>: The weather forcast of Hong Kong will be shown if no location is specified. \n 5. /stock <stock code>: The information of related stock will be displayed. \n 6. /match & /profile : Try by yourself!')
>>>>>>> 8e55542 (20250408 version K)

# default function, chatgpt Chatbot assistance
def equiped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: "+ str(Update))
    logging.info("Context: " + str(context))
    context.bot.send_message(chat_id = update.effective_chat.id, text = reply_message)

<<<<<<< HEAD

=======
# /add: add text to Redis database
def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0] # /add keyword <-- this should store the keyword
        redis1.incr(msg) 
            
        update.message.reply_text('You have said ' + msg + ' for ' + redis1.get(msg) + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

# /weather: check weather
openweather_password = os.environ['OPENWEATHER_ACCESS_TOKEN'] 
>>>>>>> 8e55542 (20250408 version K)
def weather(update: Update, context: CallbackContext) -> None:
    """Fetch current weather for a city."""
    try:
        city = context.args[0] if context.args else "Hongkong"  # Default to Hongkong if no city provided
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={openweather_password}&units=metric"
        response = requests.get(url).json()
        
        if response.get("cod") != 200:
            update.message.reply_text(f"Error: {response.get('message', 'City not found')}")
            return
        
        temp = response["main"]["temp"]
        description = response["weather"][0]["description"]
        reply = f"Current weather in {city}:\nTemperature: {temp}°C\nCondition: {description.capitalize()}"
        update.message.reply_text(reply)
    except IndexError:
        update.message.reply_text("Usage: /weather <city>")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

<<<<<<< HEAD
=======
# /forecast: forecast weather
openweather_password = os.environ['OPENWEATHER_ACCESS_TOKEN']
>>>>>>> 8e55542 (20250408 version K)
def forecast(update: Update, context: CallbackContext) -> None:
    """Fetch 5-day weather forecast for a city."""
    try:
        city = context.args[0] if context.args else "Hongkong"  # Default to Hongkong if no city provided
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={openweather_password}&units=metric"
        response = requests.get(url).json()
        
        if response.get("cod") != "200":
            update.message.reply_text(f"Error: {response.get('message', 'City not found')}")
            return
        
        daily_forecast = {}
        for entry in response["list"]:
            # Extract date from timestamp
            date = datetime.fromtimestamp(entry["dt"]).date()
            if date not in daily_forecast:
                daily_forecast[date] = {"temps": [], "conditions": []}
            daily_forecast[date]["temps"].append(entry["main"]["temp"])
            daily_forecast[date]["conditions"].append(entry["weather"][0]["description"])
        
        # Generate daily summary for 5 days
        reply = f"5-day daily forecast for {city}:\n"
        current_date = datetime.now().date()
        for i in range(5):
            forecast_date = current_date + timedelta(days=i)
            if forecast_date in daily_forecast:
                temps = daily_forecast[forecast_date]["temps"]
                conditions = daily_forecast[forecast_date]["conditions"]
                avg_temp = sum(temps) / len(temps)  # Average temperature
                dominant_condition = Counter(conditions).most_common(1)[0][0]  # Most frequent condition
                reply += f"{forecast_date}: {avg_temp:.1f}°C, {dominant_condition.capitalize()}\n"
            else:
                reply += f"{forecast_date}: No data available\n"
        
        update.message.reply_text(reply)
    except IndexError:
        update.message.reply_text("Usage: /forecast <city>")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

<<<<<<< HEAD
=======

# /stock: check stock price and the graph
>>>>>>> 8e55542 (20250408 version K)
def stock(update: Update, context: CallbackContext) -> None:
    """Fetch real-time stock data for a ticker using yFinance."""
    try:
        # Default to "0700.HK" (Tencent) if no ticker provided
        ticker_symbol = context.args[0] if context.args else "0700.HK"
        
        # Create a Ticker object with yFinance
        ticker = yf.Ticker(ticker_symbol)
        
        # Fetch the latest data (e.g., last closing price)
        stock_info = ticker.info
        if not stock_info or 'currentPrice' not in stock_info:
            update.message.reply_text(f"Error: Could not fetch data for {ticker_symbol}. Check the ticker symbol.")
            return
        
        # Extract relevant data
        price = stock_info.get('currentPrice', stock_info.get('regularMarketPrice', 'N/A'))
        company_name = stock_info.get('longName', ticker_symbol)
        
        # Send response
        update.message.reply_text(f"Latest price for {ticker_symbol} ({company_name}): {price} {stock_info.get('currency', 'USD')}")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}. Usage: /stock <ticker> (e.g., /stock 0700.HK)")

def profile(update: Update, context: CallbackContext) -> None:
    """View or update profile: /profile [name interests]"""
    try:
        user_id = str(update.effective_user.id)
        args = context.args

        if not args:
            user_data = redis1.get(user_id)
            if not user_data:
                update.message.reply_text("No profile found. Use /profile <name> <interests> to set one.")
                return
            name, interests = user_data.split(":", 1)
            update.message.reply_text(f"Your Profile:\nName: {name}\nInterests: {interests}")
            return

        if len(args) < 2:
            update.message.reply_text("Usage: /profile <name> <interest1, interest2, ...>")
            return
        
        name = args[0]
        interests = ",".join(args[1:]).lower()

        for attempt in range(3):
            try:
                redis1.ping()
                redis1.set(user_id, f"{name}:{interests}")
                break
            except redis.ConnectionError as e:
                logging.error(f"Redis retry {attempt+1} in profile: {e}")
                if attempt == 2:
                    raise
                time.sleep(1)

        update.message.reply_text(f"Profile updated:\nName: {name}\nInterests: {interests}")
    except redis.ConnectionError as e:
        logging.error(f"Redis connection error: {e}")
        update.message.reply_text("Cannot connect to the database. Try again later.")
    except Exception as e:
        logging.error(f"Error in profile: {e}")
        update.message.reply_text("Something went wrong. Try again!")

def match(update: Update, context: CallbackContext) -> None:
    """Match with a specific user by name: /match <name>"""
    try:
        user_id = str(update.effective_user.id)
        user_data = redis1.get(user_id)

        if not user_data:
            update.message.reply_text("No profile found. Use /profile <name> <interests> first.")
            return

        if not context.args:
            update.message.reply_text("Usage: /match <name>")
            return

        target_name = context.args[0].lower()
        caller_name, caller_interests = user_data.split(":", 1)
        caller_interest_list = set(caller_interests.split(","))

        # Search for the target user by name
        all_users = redis1.keys("*")
        match_found = False
        for other_user_id in all_users:
            other_data = redis1.get(other_user_id)
            if other_data:
                other_name, other_interests = other_data.split(":", 1)
                if other_name.lower() == target_name:
                    other_interest_list = set(other_interests.split(","))
                    common_interests = caller_interest_list & other_interest_list
                    if common_interests:
                        update.message.reply_text(
                            f"Match found with {other_name}:\n"
                            f"Your Interests: {caller_interests}\n"
                            f"{other_name}'s Interests: {other_interests}\n"
                            f"Common Interests: {', '.join(common_interests)}"
                        )
                        match_found = True
                    else:
                        update.message.reply_text(
                            f"No common interests with {other_name}.\n"
                            f"Your Interests: {caller_interests}\n"
                            f"{other_name}'s Interests: {other_interests}"
                        )
                        match_found = True
                    break  # Stop searching once target is found

        if not match_found:
            update.message.reply_text(f"No user named '{target_name}' found.")
    except redis.ConnectionError as e:
        logging.error(f"Redis connection error: {e}")
        update.message.reply_text("Cannot connect to the database. Try again later.")
    except Exception as e:
        logging.error(f"Error in match: {e}")
        update.message.reply_text("Something went wrong. Try again!")
<<<<<<< HEAD
=======

>>>>>>> 8e55542 (20250408 version K)

if __name__ == '__main__':
    main()