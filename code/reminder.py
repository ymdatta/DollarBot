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
        bot.send_message(chat_id, "Invalid time format. Please enter the time in the format HH:MM (e.g., 14:30)")