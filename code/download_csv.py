import helper
import logging
from telegram import InputFile
from telebot import types
import csv
import os

def run(message, bot):
    try:
        chat_id = message.chat.id
        user_history = helper.getUserHistory(chat_id)
        
        if not user_history:
            bot.send_message(chat_id, "you have no history to generate CSV file.")
            return None

        file_path = 'code/data.csv'
        column_names = ['Date and Time', 'Category', 'Amount']

        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(column_names)
            writer.writerows(csv.reader(user_history, delimiter=','))

        with open(file_path, 'rb') as file:
            bot.send_document(chat_id, document=file)
        return file_path


    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        bot.send_message(chat_id, "An unexpected error occurred. Please try again later.")