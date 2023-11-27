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
import logging
from telebot import types
from datetime import datetime

option = {}

# Main run function
def run(message, bot):
    """
    This function takes 2 arguments for processing.

    - **message** which is the message from the user on Telegram.
    - **bot** which is the telegram bot object from the main code.py function.

    This is the starting function in the implementation of account feature. It pops up a menu on the telegram asking the user to chose from two different account types, after which control is given to post_category_selection(message, bot) for further processing.
    """
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
    """
    This function takes 2 arguments for processing.

    - **message** which is the message from the user on Telegram.
    - **bot** which is the telegram bot object from the run(message, bot) function.

    This is the function which gets executed once an account type is selected. It changes current account used for expenses to the one input by the user.

    If an invalid account is selected, it erros out raising an exception indicating that the right category needs to be selected and it provides list of commands to start the next iteration.
    """
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
    """
    This function takes 2 arguments for processing.

    - **chat_id** which is the unique ID for a user provided by Telegram.
    - **type** which is the account type user selected for future purchases.

    This function is a helper function, which creates user record if it's a new user. It then updates the account type for expenses based on the inputs from the user.
    """
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

