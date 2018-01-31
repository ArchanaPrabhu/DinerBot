#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import zomato
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
import logging
from constants import Constants


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

LOCATING, SUGGEST, PRICE, CUISINE, QUERY,BACK = range(6)
cuisine_list = []


def start(bot, update):
    update.message.reply_text('Hi there I\'m Dina the Diner Bot')
    update.message.reply_text('Type /done once you\'re finished')
    bot.send_chat_action(chat_id=update.message.chat_id,action=telegram.ChatAction.TYPING)
    reply_markup = telegram.ReplyKeyboardMarkup([[telegram.KeyboardButton('Send Location', request_location=True)]],
                                                one_time_keyboard=True)
    update.message.reply_text("Before we get started, can you please share your location with me?",
                              reply_markup=reply_markup)
    return LOCATING

def back(bot, update):
    
    reply_markup = telegram.ReplyKeyboardMarkup(Constants.filter_choice_menu, one_time_keyboard=True)
   #update.message.reply_text("How would you like to filter your restaurant suggestions?", reply_markup=reply_markup)
    update.message.reply_text('Type /done if you\'re finished else pick the filter of your choice !',reply_markup=reply_markup)
    return SUGGEST

def get_location(bot, update):
    global location
    location = update.message.location
    print(location)
    global cuisine_list
    cuisine_list = zomato.get_cuisines(location)
    cuisine_list = [[i] for i in cuisine_list]
    reply_markup = telegram.ReplyKeyboardMarkup(Constants.filter_choice_menu, one_time_keyboard=True)
    update.message.reply_text("How would you like to filter your restaurant suggestions?", reply_markup=reply_markup)
    return SUGGEST


def suggest(bot, update):
    response = update.message.text
    bot.send_chat_action(chat_id=update.message.chat_id,action=telegram.ChatAction.TYPING)
   # print(response)
    if response == 'Price & Rating':
        reply_markup = telegram.ReplyKeyboardMarkup(Constants.price_choice_menu, one_time_keyboard=True)
        update.message.reply_text("Choose your price point", reply_markup=reply_markup)
        return PRICE
    elif response == 'Cuisine':
        reply_markup = telegram.ReplyKeyboardMarkup(cuisine_list, one_time_keyboard=True)
        update.message.reply_text("Which cuisine are you in the mood for? Press a button or type in your choice",
                                  reply_markup=reply_markup)
        return CUISINE
    elif response == 'Food Item':
        update.message.reply_text("What are you craving today?")
        return QUERY


def price(bot, update):
    response = update.message.text
    #print(response)
    price_range = 2
    if response == '$':
        price_range = 1
    elif response == '$$':
        price_range = 2
    elif response == '$$$':
        price_range = 3
    elif response == '$$$$':
        price_range = 4
    bot.send_chat_action(chat_id=update.message.chat_id,action=telegram.ChatAction.TYPING)
    lat, long, title, address = zomato.search_by_price(price_range)
    update.message.reply_text('Here are the top rated places within your budget')
    send_venue(bot, update, lat, long, title, address)
    back(bot,update)

def cuisine(bot, update):
    response = update.message.text
    bot.send_chat_action(chat_id=update.message.chat_id,action=telegram.ChatAction.TYPING)
    lat, long, title, address = zomato.search_by_cuisine(response)
    if not lat:
        update.message.reply_text('Sorry invalid cuisine')
    else:
        update.message.reply_text('Here are nearby places serving {} cuisine'.format(response.title()))
        send_venue(bot, update, lat, long, title, address)
    back(bot,update)

def query(bot, update):
    response = update.message.text
    bot.send_chat_action(chat_id=update.message.chat_id,action=telegram.ChatAction.TYPING)
    lat, long, title, address = zomato.search_by_query(response)    
    update.message.reply_text('Here are nearby places serving {}'.format(response.lower()))
    send_venue(bot, update, lat, long, title, address)
    back(bot,update)

def send_venue(bot, update, lat, long, title, address):
    if len(lat) == 0:
        update.message.reply_text('Sorry no matching results')
    for i in range(0, len(lat)):
        bot.sendVenue(chat_id=update.message.chat_id, latitude=lat[i], longitude=long[i], title=title[i],
                      address=address[i])
       


def done(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id,action=telegram.ChatAction.TYPING)
    bot.send_chat_action(chat_id=update.message.chat_id,action=telegram.ChatAction.TYPING)
    update.message.reply_text("Hope you enjoy your meal!")
    update.message.reply_text("Type /start to talk to me again")
    return ConversationHandler.END


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater('491326980:AAEAG7Q0nBiqMSb1Ln7qqdhAGw6_SZJUfMA')

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LOCATING: [MessageHandler(Filters.location, get_location)],
            BACK:[MessageHandler(Filters.text, back)],
            SUGGEST: [MessageHandler(Filters.text, suggest)],
            PRICE: [MessageHandler(Filters.text, price)],
            CUISINE: [MessageHandler(Filters.text, cuisine)],
            QUERY: [MessageHandler(Filters.text, query)],
        },
        fallbacks=[CommandHandler('done', done)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
