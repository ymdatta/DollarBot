import helper
import logging
from telebot import types
from datetime import datetime

option = {}

# Main run function
def run(message, bot):
    helper.read_json()
    chat_id = message.chat.id
    option.pop(chat_id, None)  # remove temp choice
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    print("Account Categories:")
    for c in helper.getAccountCategories():
        print("\t", c)
        markup.add(c)
    msg = bot.reply_to(message, 'Select Category', reply_markup = markup)
    bot.register_next_step_handler(msg, post_category_selection, bot)

# Contains step to run after the category is selected
def post_category_selection(message, bot):
    try:
        chat_id = message.chat.id
        selected_category = message.text
        if selected_category not in helper.getAccountCategories():
            bot.send_message(chat_id, 'Invalid', reply_markup=types.ReplyKeyboardRemove())
            raise Exception("Sorry I don't recognize this category \"{}\"!".format(selected_category))

        # Update current user's account expense type.
        helper.write_json(add_account_record(chat_id, selected_category))
        bot.send_message(chat_id, "Expenses account changed to: {}.".format(selected_category))
    except Exception as e:
        logging.exception(str(e))
        bot.reply_to(message, 'Oh no! ' + str(e))
        display_text = ""
        commands = helper.getCommands()
        for c in commands:  # generate help text out of the commands dictionary defined at the top
            display_text += "/" + c + ": "
            display_text += commands[c] + "\n"
        bot.send_message(chat_id, 'Please select a menu option from below:')
        bot.send_message(chat_id, display_text)

def add_account_record(chat_id, type):
    user_list = helper.read_json()
    if str(chat_id) not in user_list:
        user_list[str(chat_id)] = helper.createNewUserRecord()

    if type == 'Checking':
        user_list[str(chat_id)]['account']['Checking'] = "True"
        user_list[str(chat_id)]['account']['Savings'] = "False"
    else:
        user_list[str(chat_id)]['account']['Checking'] = "False"
        user_list[str(chat_id)]['account']['Savings'] = "True"

    return user_list

