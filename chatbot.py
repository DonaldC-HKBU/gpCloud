from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext)
from ChatGPT_HKBU import HKBU_ChatGPT 
#import configparser
import logging
import redis
import os
import requests
#from dotenv import load_dotenv 
#load_dotenv('token.env')
## weather function library
from datetime import datetime, timedelta
from collections import Counter
## check stock price
from futu import *

global futu_trd_ctx


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
    # check stock price
    dispatcher.add_handler(CommandHandler("quote", quote))
    dispatcher.add_handler(CommandHandler("trade", trade))
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
        
def quote(update: Update, context: CallbackContext) -> None:
    config = context.bot_data.get('config')
    if not config:
        update.message.reply_text("Error: Configuration not loaded.")
        return
    
    try:
        futu_host = config['FUTU']['HOST']
        futu_port = int(config['FUTU']['PORT'])
        
        quote_ctx = OpenQuoteContext(host=futu_host, port=futu_port)
        
        stock_code = "HK.00700" if not context.args else f"HK.{context.args[0]}"
        ret, data = quote_ctx.get_market_snapshot([stock_code])
        
        if ret == 0:
            last_price = data['last_price'][0]
            update.message.reply_text(f"Latest price for {stock_code}: {last_price} HKD")
        else:
            update.message.reply_text(f"Error fetching quote: {data}")
        
        quote_ctx.close()
    except KeyError:
        update.message.reply_text("Error: FUTU section or keys missing in config.ini.")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

def trade(update: Update, context: CallbackContext) -> None:
    """Place a simple trade using Futu API."""
    try:
        stock_code = context.args[0]  # e.g., "HK.00700"
        qty = int(context.args[1])    # Quantity to trade
        price = float(context.args[2])  # Limit price
        
        ret, data = futu_trd_ctx.place_order(
            price=price,
            qty=qty,
            code=stock_code,
            trd_side=TrdSide.BUY,  # Change to SELL if needed
            order_type=OrderType.NORMAL,
            trd_env=TrdEnv.REAL  # Use TrdEnv.SIMULATE for paper trading
        )
        
        if ret == RET_OK:
            update.message.reply_text(f"Order placed successfully: {data['order_id'][0]}")
        else:
            update.message.reply_text(f"Trade failed: {data}")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /trade <stock_code> <quantity> <price> (e.g., /trade HK.00700 100 500.0)")


if __name__ == '__main__':
    main() 