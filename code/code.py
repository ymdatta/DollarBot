"""

MIT License

Copyright (c) 2021 Dev Kumar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import telebot
import time
import helper
import edit
import history
import display
from reminder import check_reminders
import estimate
import delete
import add
import add_balance
import budget
import category
import download_csv
import download_pdf
import email_history
import add_recurring
import delete_expense
import account
from datetime import datetime
from jproperties import Properties
from telebot import types
import reminder
from datetime import datetime, time
import threading
import time

configs = Properties()

with open('user.properties', 'rb') as read_prop:
    configs.load(read_prop)

api_token = str(configs.get('api_token').data)

bot = telebot.TeleBot(api_token)

telebot.logger.setLevel(logging.INFO)

# Define listener for requests by user
def listener(user_requests):
    for req in user_requests:
        if req.content_type == 'text':
            print("{} name:{} chat_id:{} \nmessage: {}\n".format(
                str(datetime.now()), str(req.chat.first_name), str(req.chat.id), str(req.text)))


bot.set_update_listener(listener)


# Define your list of commands and descriptions
menu_commands = [
    ("add_balance", "Add balance to a specific account"),
    ("add", "Record/Add a new spending"),
    ("add_recurring", "Record the recurring expenses"),
    ("display", "Show sum of expenditure"),
    ("estimate", "Show an estimate of expenditure"),
    ("history", "Display spending history"),
    ("delete", "Clear/Erase your records"),
    ("delete_all", "Clear/Erase all your records"),
    ("edit", "Edit/Change spending details"),
    ("budget", "Add/Update/View/Delete budget"),
    ("category", "Add/Delete/Show custom categories in telegram bot"),
    ("csv", "To download your history in csv format"),
    ("pdf", "Generates a PDF file containing the user's expense history plot"),
    ("email_history", "your spend history will be sent to provided email address"),
    ("set_reminder", "Create a reminder for your purchases or bills"),
    ("select_expenses_account", "Select account to use for expenses")
]

bot.set_my_commands([
    types.BotCommand(command=command, description=description) for command, description in menu_commands
])

# Define a function to handle the /start and /menu commands
@bot.message_handler(commands=['start', 'menu'])
def start_and_menu_command(message):
    chat_id = message.chat.id
    text_intro = "Welcome to MyDollarBot! Please select an option:"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for command, _ in menu_commands:
        markup.add(types.KeyboardButton(f'/{command}'))

    bot.send_message(chat_id, text_intro, reply_markup=markup)

# Define command handlers for each menu option
@bot.message_handler(commands=[command for command, _ in menu_commands])
def handle_menu_command(message):
    command = message.text[1:]  # Remove the '/' character from the command
    if command == "add":
        add.run(message, bot)
    elif command == "add_balance":
        add_balance.run(message, bot)
    elif command == "display":
        display.run(message, bot)
    elif command == 'estimate':
        estimate.run(message, bot)
    elif command == 'add_recurring':
        add_recurring.run(message, bot)
    elif command == 'delete_all':
        delete.run(message, bot)
    elif command == 'delete':
        delete_expense.run(message, bot)
    elif command == 'budget':
        budget.run(message, bot)
    elif command == 'edit':
        edit.run(message, bot)
    elif command == 'history':
        history.run(message, bot)
    elif command == 'category':
        category.run(message, bot)
    elif command == 'csv':
        download_csv.run(message, bot)
    elif command == 'email_history':
        email_history.run(message, bot)
    elif command == 'select_expenses_account':
        account.run(message, bot)
    elif command == 'pdf':
        download_pdf.run(message, bot)
    elif command == 'set_reminder':
        print('Setting reminder')
        reminder.run(message, bot)


# Define a function to periodically check reminders
def reminder_checker():
    while True:
        check_reminders(bot)
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
