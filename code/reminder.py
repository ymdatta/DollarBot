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

import helper
from datetime import datetime, time
import time
from telebot import types
import json
import display


def run(message, bot):
    helper.read_json()
    chat_id = message.chat.id
    history = helper.getUserHistory(chat_id)
    if history is None or history == []:
        bot.send_message(chat_id, "Sorry, there are no records of spending!")
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row_width = 2
        for mode in helper.getSpendDisplayOptions():
            markup.add(mode)
        msg = bot.reply_to(message, 'Please select a category to set reminders for', reply_markup=markup)
        bot.register_next_step_handler(msg, process_reminder_type, chat_id, bot)

def process_reminder_type(message, chat_id, bot):
    selected_type = message.text
    bot.send_message(chat_id, 'Please enter the time for the reminder in the format HH:MM (e.g., 14:30)')
    bot.register_next_step_handler(message, process_reminder_time, chat_id, selected_type, bot)

def process_reminder_time(message, chat_id, selected_type, bot):
    reminder_time_str = message.text
    if helper.validate_time_format(reminder_time_str):
        with open("expense_record.json", "r") as file:
            json_data = json.load(file)

        if str(chat_id) in json_data:
            json_data[str(chat_id)]["reminder"]["type"] = selected_type
            json_data[str(chat_id)]["reminder"]["time"] = reminder_time_str

            with open("expense_record.json", "w") as file:
                json.dump(json_data, file, indent=4)

        bot.send_message(chat_id, f"Your {selected_type} expenses reminder has been set for {reminder_time_str}.")
    else:
        bot.send_message(chat_id, "Invalid time format. Please try /set_reminder with the time in the format HH:MM (e.g., 14:30)")


sent_reminders = {}


def send_expenses_reminder(chat_id, dayormonth, bot):
    history = helper.getUserHistory(chat_id)
    if history is None or history == []:
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

def send_reminder(chat_id, message, bot):
    print(f"Sending reminder to chat ID {chat_id}: {message}")
    bot.send_message(chat_id, message)

def check_reminders(bot):
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
                if (chat_id, current_date, str(reminder_time.hour) + ":" + str(reminder_time.minute)) not in sent_reminders:
                    # Send a daily reminder
                    message = "Your daily reminder message goes here."
                    print(f"Sending reminder to chat ID {chat_id}: {message}")
                    # send_reminder(chat_id, message)
                    send_expenses_reminder(chat_id, reminder_type, bot)
                    # Mark this reminder as sent
                    sent_reminders[(chat_id, current_date, str(reminder_time.hour) + ":" + str(reminder_time.minute))] = True
                    print(sent_reminders)
