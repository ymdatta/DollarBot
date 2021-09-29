#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import json
import logging
import re
import os
import telebot
import time
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

api_token = "<API_KEY>"

dateFormat = '%d-%b-%Y'
timeFormat = '%H:%M'
monthFormat = '%b-%Y'

#global variables to store user choice, user list, spend categories, etc
option = {}
user_list = {}
spend_categories = ['Food', 'Groceries', 'Transport', 'Shopping']
spend_display_option = ['Day', 'Month']

#set of implemented commands and their description
commands = {
    'menu': 'Display this menu',
    'add': 'Record/Add a new spending',
    'display': 'Show sum of expenditure for the current day/month',
    'history': 'Display spending history',
    'delete': 'Clear/Erase all your records',
    'edit': 'Edit/Change spending details'
}

bot = telebot.TeleBot(api_token)

#methods for various functionalities to be implemented here


#function to load .json expense record data
def read_json():
	global user_list
	try:
		if os.stat('expense_record.json').st_size!=0:
			with open('expense_record.json') as expense_record:
				expense_record = json.load(expense_record)
			global user_list = expense_record
	except FileNotFoundError:
		print("---------NO RECORDS FOUND---------")

#function to fetch expenditure history of the user
@bot.message_handler(commands=['history'])
def show_history(message):

#function to display total expenditure
@bot.message_handler(commands=['display'])
def command_display(message):
    read_json()
    chat_id = message.chat.id
    history = getUserHistory
    if history == None:
        bot.send_message(chat_id, "Oops! Looks like you do not have any spending records!")
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row_width = 2
        for mode in spend_display_option:
            markup.add(mode)
        # markup.add('Day', 'Month')
        msg = bot.reply_to(message, 'Please select a category to see the total expense', reply_markup=markup)
        bot.register_next_step_handler(msg, display_total)

def display_total(message):
    try:
        chat_id = message.chat.id
        DayWeekMonth = message.text

        if not DayWeekMonth in spend_display_option:
            raise Exception("Sorry I can't show spendings for \"{}\"!".format(DayWeekMonth))

        history = getUserHistory(chat_id)
        if history is None:
            raise Exception("Oops! Looks like you do not have any spending records!")

        bot.send_message(chat_id, "Hold on! Gathering my thoughts...")
        bot.send_chat_action(chat_id, 'typing')  # show the bot "typing" (max. 5 secs)
        time.sleep(0.5)

        total_text = ""

        if DayWeekMonth == 'Day':
            query = datetime.now().today().strftime(dateFormat)
            queryResult = [value for index, value in enumerate(history) if str(query) in value] #query all that contains today's date
        elif DayWeekMonth == 'Month':
            query = datetime.now().today().strftime(monthFormat)
            queryResult = [value for index, value in enumerate(history) if str(query) in value] #query all that contains today's date
        total_text = calculate_spendings(queryResult)

        spending_text = ""
        if len(total_text) == 0:
            spending_text = "You have no spendings for {}!".format(DayWeekMonth)
        else:
            spending_text = "Here are your total spendings {}:\nCATEGORIES,AMOUNT \n----------------------\n{}".format(DayWeekMonth.lower(), total_text)

        bot.send_message(chat_id, spending_text)
    except Exception as e:
        bot.reply_to(message, 'Exception! Please try again' + str(e))

def calculate_spendings(queryResult):
    total_dict = {}

    for row in queryResult:
        s = row.split(',')    #date,cat,money
        cat = s[1]  #cat
        if cat in total_dict:
            total_dict[cat] = round(total_dict[cat] + float(s[2]),2)    #round up to 2 decimal
        else:
            total_dict[cat] = float(s[2])
    total_text = ""
    for key, value in total_dict.items():
        total_text += str(key) + " $" + str(value) + "\n"
    return total_text

def getUserHistory(chat_id):
    global global_users_dict
    if (str(chat_id) in global_users_dict):
        return global_users_dict[str(chat_id)]
    return None

def main():
    try:
        bot.polling(none_stop=True)
    except Exception:
        time.sleep(3)
        print("Connection Timeout")

if __name__ == '__main__':
    main()
