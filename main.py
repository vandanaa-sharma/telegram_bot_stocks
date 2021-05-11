
import configparser
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.parsemode import ParseMode
from bs4 import BeautifulSoup
import requests
from datetime import date
import time

config = configparser.ConfigParser()
config.read('config')
API_KEY = config['TELEGRAM']['API_KEY']
PORT = config["TELEGRAM"]['PORT']


urls = {
    "stocks" : "https://www.moneycontrol.com/rss/buzzingstocks.xml",
    "topnews": "https://www.moneycontrol.com/rss/MCtopnews.xml",
    "currency": "https://www.moneycontrol.com/rss/currency.xml",
    "ipo": "https://www.moneycontrol.com/rss/iponews.xml",
    "mf": "https://www.moneycontrol.com/rss/mfnews.xml"
} 

def start(update, context):
    user_name = str(update.message.chat.first_name)
    context.bot.send_message(chat_id=update.message.chat_id,
                     text="Hello <b>" + user_name + "</b>, welcome to Stock Market Feed!",
                     parse_mode = ParseMode.HTML)
    send_options(update)

def send_options(update:Update):
    keyboard = [
        [
            InlineKeyboardButton("Mutual Funds", callback_data='mf'),
            InlineKeyboardButton("Top News", callback_data='topnews') 
        ],
        [
            InlineKeyboardButton("Currency", callback_data='currency'),
            InlineKeyboardButton("IPO", callback_data='ipo')
        ],
        [
            InlineKeyboardButton("Stocks", callback_data='stocks')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please select one of the following options:', reply_markup=reply_markup)

def send_feed(update : Update, context : CallbackContext, url):
    r = requests.get(url, cert=('keys/certificate.crt', 'keys/private.key'))
    if r.status_code == 200 :
        soup = BeautifulSoup(r.content.decode("utf-8"), features='html.parser')
        items = soup.findAll('item')
        articles = []
        for a in items:
            title = a.find('title').text
            desc = a.find('description').text
            article = {
                'title': title,
                'desc': desc
                }
            articles.append(article)
    for i in range(3):
        if(articles[i] != None):
            message = str("<b>") + str(articles[i]['title']) + str("</b>")
            context.bot.send_message(
                            chat_id=update.effective_chat.id, 
                            text=message, 
                            parse_mode=ParseMode.HTML,
                    )
            desc_alt = str(" - ") + str(articles[i]['desc']).split("=")[-1].split(">")[-1]
            context.bot.send_message(
                            chat_id=update.effective_chat.id, 
                            text=str(" - ") + str(articles[i]['desc']).split("=")[-1].split(">")[-1], 
                            parse_mode=ParseMode.HTML
            )
            context.bot.send_message(
                            chat_id=update.effective_chat.id, 
                            text=str("--------------------------------------------------------------"), 
                            parse_mode=ParseMode.HTML
            )
    update.callback_query.answer()

def button(update: Update, context : CallbackContext):
    query = update.callback_query
    try:
        send_feed(update, context, urls[query.data])
    except:
        update.callback_query.reply_text("Oops! Something went wrong!")
        send_options(update)
        update.callback_query.answer()
       
def help(update, context):
    pass

def error(update, context):
    # print('Update "%s" caused error "%s"', update, context.error)
    pass

def echo(update, context):
    send_options(update)

if __name__ == '__main__':

    updater = Updater(API_KEY, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(CallbackQueryHandler(button))
 
    dp.add_error_handler(error)

    updater.start_polling()

    # updater.start_webhook(listen="0.0.0.0",
    #                       port=int(PORT),
    #                       url_path=API_KEY,
    #                       key='keys/private.key',
    #                       cert='keys/certificate.crt',
    #                       webhook_url='https://telegram-bot-stocks.herokuapp.com/' + API_KEY)
    
    # time.sleep(1)

    # updater.bot.setWebhook('https://telegram-bot-stocks.herokuapp.com/' + API_KEY)

    updater.idle()
