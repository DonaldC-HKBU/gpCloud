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


if __name__ == '__main__':
    main() 