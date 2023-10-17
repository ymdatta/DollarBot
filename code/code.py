#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import telebot
import time
import helper
import edit
import history
import display
import estimate
import delete
import add
import budget
import category
import add_recurring
from datetime import datetime
from jproperties import Properties
import reminder
import json
from datetime import datetime, time
import threading
import time

configs = Properties()

with open('user.properties', 'rb') as read_prop:
    configs.load(read_prop)

api_token = str(configs.get('api_token').data)

bot = telebot.TeleBot(api_token)

telebot.logger.setLevel(logging.INFO)

option = {}


# Define listener for requests by user
def listener(user_requests):
    for req in user_requests:
        if(req.content_type == 'text'):
            print("{} name:{} chat_id:{} \nmessage: {}\n".format(str(datetime.now()), str(req.chat.first_name), str(req.chat.id), str(req.text)))


bot.set_update_listener(listener)


# defines how the /start and /help commands have to be handled/processed
@bot.message_handler(commands=['start', 'menu'])
def start_and_menu_command(m):
    helper.read_json()
    global user_list
    chat_id = m.chat.id

    text_intro = "Welcome to MyDollarBot - a simple solution to track your expenses and manage them ! \nPlease select the options from below for me to assist you with: \n\n"
    commands = helper.getCommands()
    for c in commands:  # generate help text out of the commands dictionary defined at the top
        text_intro += "/" + c + ": "
        text_intro += commands[c] + "\n"
    bot.send_message(chat_id, text_intro)
    return True


# defines how the /new command has to be handled/processed
# function to add an expense
@bot.message_handler(commands=['add'])
def command_add(message):
    add.run(message, bot)


# function to add recurring expenses
@bot.message_handler(commands=['add_recurring'])
def command_add_recurring(message):
    add_recurring.run(message, bot)
    
    
# function to fetch expenditure history of the user
@bot.message_handler(commands=['history'])
def command_history(message):
    history.run(message, bot)


# function to edit date, category or cost of a transaction
@bot.message_handler(commands=['edit'])
def command_edit(message):
    edit.run(message, bot)


# function to display total expenditure
@bot.message_handler(commands=['display'])
def command_display(message):
    display.run(message, bot)


# function to estimate future expenditure
@bot.message_handler(commands=['estimate'])
def command_estimate(message):
    estimate.run(message, bot)


# handles "/delete" command
@bot.message_handler(commands=['delete'])
def command_delete(message):
    delete.run(message, bot)

# handles "/budget" command
@bot.message_handler(commands=['budget'])
def command_budget(message):
    budget.run(message, bot)

# handles "/category" command
@bot.message_handler(commands=['category'])
def command_category(message):
    category.run(message, bot)

# not used
def addUserHistory(chat_id, user_record):
    global user_list
    if(not(str(chat_id) in user_list)):
        user_list[str(chat_id)] = []
    user_list[str(chat_id)].append(user_record)
    return user_list

# function to create and display a reminder
@bot.message_handler(commands=['setReminder'])
def command_display(message):
    reminder.run(message, bot)


sent_reminders = {}

def send_expenses_reminder(chat_id, dayormonth):
    history = helper.getUserHistory(chat_id)
    if history is None:
        raise Exception("Oops! Looks like you do not have any spending records!")

    bot.send_message(chat_id, "Your Daily Expense Reminder...")
    # show the bot "typing" (max. 5 secs)
    bot.send_chat_action(chat_id, 'typing')
    time.sleep(0.5)
    total_text = ""
    # get budget data
    budgetData = {}
    if helper.isOverallBudgetAvailable(chat_id):
        budgetData = helper.getOverallBudget(chat_id)
    elif helper.isCategoryBudgetAvailable(chat_id):
        budgetData = helper.getCategoryBudget(chat_id)

    if dayormonth == 'Day':
        query = datetime.now().today().strftime(helper.getDateFormat())
        # query all that contains today's date
        queryResult = [value for index, value in enumerate(history) if str(query) in value]
    elif dayormonth == 'Month':
        query = datetime.now().today().strftime(helper.getMonthFormat())
        # query all that contains today's date
        queryResult = [value for index, value in enumerate(history) if str(query) in value]
    
    total_text = display.calculate_spendings(queryResult)
    spending_text = display.display_budget_by_text(history, budgetData)
    if len(total_text) == 0:
        spending_text += "----------------------\nYou have no spendings for {}!".format(dayormonth)
        bot.send_message(chat_id, spending_text)
    else:
        spending_text += "\n----------------------\nHere are your total spendings {}:\nCATEGORIES,AMOUNT \n----------------------\n{}".format(dayormonth.lower(), total_text)
        bot.send_message(chat_id, spending_text)

def send_reminder(chat_id, message):
    print(f"Sending reminder to chat ID {chat_id}: {message}")
    bot.send_message(chat_id, message)

def check_reminders():
    print("Checking reminders...")
    # Load the JSON data
    with open("expense_record.json", "r") as file:
        json_data = json.load(file)

    current_time = datetime.now().time()
    current_date = datetime.now().strftime('%d-%b-%Y')  # Get the current date in the same format as your data

    # Loop through the chat IDs and their reminders
    for chat_id, data in json_data.items():
        reminder = data.get("reminder")
        if reminder and reminder.get("time"):
            reminder_time = datetime.strptime(reminder["time"], '%H:%M').time()
            # Compare the time components without seconds
            if current_time.hour == reminder_time.hour and current_time.minute == reminder_time.minute:
                reminder_type = reminder.get("type")
                if (chat_id, current_date, str(reminder_time.hour)+":"+str(reminder_time.minute)) not in sent_reminders:
                    # Send a daily reminder
                    message = "Your daily reminder message goes here."
                    print(f"Sending reminder to chat ID {chat_id}: {message}")
                    # send_reminder(chat_id, message)
                    send_expenses_reminder(chat_id, reminder_type)
                    # Mark this reminder as sent
                    sent_reminders[(chat_id, current_date, str(reminder_time.hour)+":"+str(reminder_time.minute))] = True
                    print(sent_reminders)

# Define a function to periodically check reminders
def reminder_checker():
    while True:
        check_reminders()
        # Sleep for one minute
        time.sleep(60)

# The main function
def main():
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.exception(str(e))
        time.sleep(3)
        print("Connection Timeout")


if __name__ == '__main__':
    reminder_thread = threading.Thread(target=reminder_checker)
    reminder_thread.daemon = True
    reminder_thread.start()

    main()
