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

def main():
    try:
        bot.polling(none_stop=True)
    except Exception:
        time.sleep(3)
        print("Connection Timeout")


if __name__ == '__main__':
    main()
