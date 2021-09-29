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
def load_Json():
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
	


def main():
    try:
        bot.polling(none_stop=True)
    except Exception:
        time.sleep(3)
        print("Connection Timeout")

if __name__ == '__main__':
    main()
