from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext)
from ChatGPT_HKBU import HKBU_ChatGPT 
import configparser
import logging
import redis
import os
import requests
#from dotenv import load_dotenv 
#load_dotenv('token.env')

## weather function library ##
from datetime import datetime, timedelta
from collections import Counter
## check stock price with the yFinance##
import yfinance as yf
import matplotlib.pyplot as plt


def main():
    # Load your token and create an Updater for your Bot
    #config = configparser.ConfigParser()
    #config.read('config.ini')
    #updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True) - used for config.ini
    updater = Updater(token=(os.environ['TELEGRAM_ACCESS_TOKEN']), use_context=True) #- used for fly.io/Azure
    #used for docker below
    #updater = Updater(token=(os.getenv('TELEGRAM_ACCESS_TOKEN')), use_context=True)

    dispatcher = updater.dispatcher
    global redis1
    redis_host = "redis-18364.c1.asia-northeast1-1.gce.redns.redis-cloud.com"
    redis_port = 18364
    redis_password = os.environ['REDIS_ACCESS_TOKEN'] 
    #used for docker below
    #redis_password = os.getenv('REDIS_ACCESS_TOKEN')
    redis1 = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password)
    # You can set this logging module, so you will know when
    # and why things do not work as expected Meanwhile, update your config.ini as:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    # register a dispatcher to handle message: here we register an echo dispatcher
    #echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    #dispatcher.add_handler(echo_handler)
    # dispatcher for chatgpt
    global chatgpt
    chatgpt = HKBU_ChatGPT()
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command),equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)
    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add",add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    # answer when using /hello
    dispatcher.add_handler(CommandHandler("hello", hello))
    # check weather and forecast weather
    dispatcher.add_handler(CommandHandler("weather", weather))
    dispatcher.add_handler(CommandHandler("forecast", forecast))
    # check stock price and the graph
    dispatcher.add_handler(CommandHandler("stock", stock))
    # To start the bot:
    updater.start_polling()
    updater.idle()

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
def hello(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /hello is issued."""
    msg = context.args[0]
    update.message.reply_text('Good day,'+ msg +'!')

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')

def equiped_chatgpt(update, context):
    global chatgpt
    try:
        reply_message = chatgpt.submit(update.message.text)
        logging.info("Update: " + str(update))
        logging.info("context: " + str(context))
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
    except Exception as e:
        logging.exception("Error while processing the message: ")
        context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred. Please try again later.")


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

# check weather
def weather(update: Update, context: CallbackContext) -> None:
    """Fetch current weather for a city."""
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config['OPENWEATHER']['API_KEY']
    
    try:
        city = context.args[0] if context.args else "Hongkong"  # Default to Hongkong if no city provided
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
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

# forecast weather
def forecast(update: Update, context: CallbackContext) -> None:
    """Fetch 5-day weather forecast for a city."""
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config['OPENWEATHER']['API_KEY']
    
    try:
        city = context.args[0] if context.args else "Hongkong"  # Default to Hongkong if no city provided
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
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


# check stock price and the graph
def stock(update: Update, context: CallbackContext) -> None:
    """Fetch stock data and plot a graph using yfinance."""
    try:
        stock_code = context.args[0] if context.args else "0700.HK"  # Default to Tencent
        period = context.args[1] if len(context.args) > 1 else "1mo"  # Default to 1 month (e.g., "1d", "5d", "1mo", "1y")
        
        # Fetch stock data
        stock = yf.Ticker(stock_code)
        info = stock.info  # Basic info
        hist = stock.history(period=period)  # Historical data
        
        if not info or 'longName' not in info or hist.empty:
            update.message.reply_text(f"No data found for {stock_code}. Ensure the ticker is correct.")
            return
        
        stock_name = info['longName']
        price = info['regularMarketPrice']  # Current price
        currency = info['currency']
        
        # Send current price as text
        update.message.reply_text(f"Stock: {stock_name} ({stock_code})\nPrice: {price} {currency}")
        
        # Plot the closing price
        plt.figure(figsize=(10, 5))
        plt.plot(hist.index, hist['Close'], label=f"{stock_name} Closing Price")
        plt.title(f"{stock_name} ({stock_code}) - {period} Price History")
        plt.xlabel("Date")
        plt.ylabel(f"Price ({currency})")
        plt.legend()
        plt.grid(True)
        
        # Save the plot as an image
        graph_file = f"{stock_code}_graph.png"
        plt.savefig(graph_file)
        plt.close()  # Close the figure to free memory
        
        # Send the graph image via Telegram
        with open(graph_file, 'rb') as photo:
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
        
        # Optional: Clean up the file after sending
        import os
        os.remove(graph_file)
        
    except IndexError:
        update.message.reply_text("Usage: /stock <stock_code> [period] (e.g., /stock 0700.HK 1mo)")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main() 