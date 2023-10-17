import helper
import logging
import telebot
import threading
import datetime
from telebot import types
import json


def run(message, bot):
    helper.read_json()
    chat_id = message.chat.id
    history = helper.getUserHistory(chat_id)
    if history is None:
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

    with open("expense_record.json", "r") as file:
        json_data = json.load(file)

    if str(chat_id) in json_data:
        json_data[str(chat_id)]["reminder"]["type"] = selected_type
        json_data[str(chat_id)]["reminder"]["time"] = reminder_time_str

        with open("expense_record.json", "w") as file:
            json.dump(json_data, file, indent=4)

    bot.send_message(chat_id, f"Reminder type set to: {selected_type}")
    bot.send_message(chat_id, f"Reminder time set to: {reminder_time_str}")

# def process_reminder_time(message, user_id, bot):
#     chat_id = reminders[user_id]['chat_id']
#     reminder_text = reminders[user_id]['text']
#     reminder_time_str = message.text
#     try:
#         reminder_time = datetime.strptime(reminder_time_str, "%H:%M")
#         current_time = datetime.now()
#         time_difference = (reminder_time - current_time).total_seconds()
#         if time_difference < 0:
#             bot.send_message(chat_id, "Invalid time. Please enter a future time.")
#             return
#         bot.send_message(chat_id, f"Reminder set for {reminder_time_str}.")
#         # Schedule the reminder to trigger at the specified time
#         threading.Timer(time_difference, send_reminder, args=[chat_id, reminder_text]).start()
#     except ValueError:
#         bot.send_message(chat_id, "Invalid time format. Please use HH:MM format.", bot)

# def send_reminder(chat_id, reminder_text, bot):
#     bot.send_message(chat_id, f"Reminder: {reminder_text}")