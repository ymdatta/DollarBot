#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import json
import logging
import re
import os
import telebot
import time
from telebot import types
from datetime import datetime

api_token = "1925990647:AAHkeYbE7CU8BdR9d-ge2PepdhNvqAFxwKA"

dateFormat = '%d-%b-%Y'
timeFormat = '%H:%M'
monthFormat = '%b-%Y'

#global variables to store user choice, user list, spend categories, etc
option = {}
user_list = {}
spend_categories = ['Food', 'Groceries', 'Utilities', 'Transport', 'Shopping', 'Miscellaneous']
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

telebot.logger.setLevel(logging.INFO)

#Define listener
#bot.set_update_listener(listener)

#defines how the /start and /help commands have to be handled/processed
@bot.message_handler(commands=['start', 'menu'])
def start_and_menu_command(m):
    read_json()
    global user_list
    chat_id = m.chat.id

    text_intro = "Welcome to TrackMyDollar - a simple solution to track your expenses! \nHere is a list of available commands, please enter a command of your choice so that I can assist you further: \n\n"
    for c in commands:  # generate help text out of the commands dictionary defined at the top
        text_intro += "/" + c + ": "
        text_intro += commands[c] + "\n\n"
    bot.send_message(chat_id, text_intro)

#defines how the /new command has to be handled/processed
@bot.message_handler(commands=['add'])
def command_add(message):
    read_json()
    chat_id = message.chat.id
    option.pop(chat_id, None)  # remove temp choice
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    for c in spend_categories:
        markup.add(c)
    msg = bot.reply_to(message, 'Select Category', reply_markup=markup)
    bot.register_next_step_handler(msg, post_category_selection)

def post_category_selection(message):
        try:
            chat_id = message.chat.id
            selected_category = message.text
            if not selected_category in spend_categories:
                msg = bot.send_message(chat_id, 'Invalid', reply_markup=types.ReplyKeyboardRemove())
                raise Exception("Sorry I don't recognise this category \"{}\"!".format(selected_category))

            option[chat_id] = selected_category
            message = bot.send_message(chat_id, 'How much did you spend on {}? \n(Enter numeric values only)'.format(str(option[chat_id])))
            bot.register_next_step_handler(message, post_amount_input)
        except Exception as e:
            bot.reply_to(message, 'Oh no! ' + str(e))
            display_text = ""
            for c in commands:  # generate help text out of the commands dictionary defined at the top
                display_text += "/" + c + ": "
                display_text += commands[c] + "\n"
            bot.send_message(chat_id, 'Please select a menu option from below:')
            bot.send_message(chat_id, display_text)

def post_amount_input(message):
    try:
        chat_id = message.chat.id
        amount_entered = message.text
        amount_value = validate_entered_amount(amount_entered)  # validate
        if amount_value == 0:  # cannot be $0 spending
            raise Exception("Spent amount has to be a non-zero number.")

        date_of_entry = datetime.today().strftime(dateFormat + ' ' + timeFormat)
        date_str, category_str, amount_str = str(date_of_entry), str(option[chat_id]), str(amount_value)
        write_json(add_user_record(chat_id, "{},{},{}".format(date_str, category_str, amount_str)))
        bot.send_message(chat_id, 'The following expenditure has been recorded: You have spent ${} for {} on {}'.format(amount_str, category_str, date_str))

    except Exception as e:
        bot.reply_to(message, 'Oh no. ' + str(e))

def validate_entered_amount(amount_entered):
    if len(amount_entered) > 0 and len(amount_entered) <= 15:
        if amount_entered.isdigit:
            if re.match("^[0-9]*\\.?[0-9]*$", amount_entered):
                amount = round(float(amount_entered), 2)
                if amount > 0:
                    return str(amount)
    return 0

def write_json(user_list):
    try:
        with open('data.json', 'w') as json_file:
            json.dump(user_list, json_file, ensure_ascii=False, indent=4)
    except FileNotFoundError:
        print('Sorry, the data.json file could not be found.')

def add_user_record(chat_id, record_to_be_added):
    global user_list
    if not (str(chat_id) in user_list):
        user_list[str(chat_id)] = []

    user_list[str(chat_id)].append(record_to_be_added)
    return user_list

#function to load .json expense record data
def read_json():
    global user_list
    try:
        if os.stat('expense_record.json').st_size!=0:
            with open('expense_record.json') as expense_record:
                expense_record = json.load(expense_record)
                user_list = expense_record
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
    global user_list
    if (str(chat_id) in user_list):
        return user_list[str(chat_id)]
    return None

def main():
    try:
        bot.polling(none_stop=True)
    except Exception:
        time.sleep(3)
        print("Connection Timeout")

if __name__ == '__main__':
    main()
