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
from forex_python.converter import CurrencyRates

option = {}
currencies = CurrencyRates(force_decimal = False)

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

def post_category_selection(message, bot):
    try:
        chat_id = message.chat.id
        selected_category = message.text
        if selected_category not in helper.getAccountCategories():
            bot.send_message(chat_id, 'Invalid', reply_markup=types.ReplyKeyboardRemove())
            raise Exception("Sorry I don't recognize this account category \"{}\"!".format(selected_category))

        option[chat_id] = selected_category
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row_width = 2
        print("Currencies:")
        for c in helper.getCurrencies():
            print("\t", c)
            markup.add(c)
        msg = bot.reply_to(message, 'Select Currency', reply_markup = markup)
        bot.register_next_step_handler(msg, post_currency_selection, bot, selected_category)
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

# Contains step to run after the currency is selected
def post_currency_selection(message, bot, selected_category):
    try:
        chat_id = message.chat.id
        selected_currency = message.text
        if selected_currency not in helper.getCurrencies():
            bot.send_message(chat_id, 'Invalid', reply_markup=types.ReplyKeyboardRemove())
            raise Exception("Sorry I don't recognize this currency \"{}\"!".format(selected_currency))

        message = bot.send_message(chat_id, 'How much money you want to add in {} account? \n(Enter numeric values only)'.format(str(option[chat_id])))
        bot.register_next_step_handler(message, post_amount_input, bot, selected_category, selected_currency)
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

# Contains step to run after the amount is inserted
def post_amount_input(message, bot, selected_category, selected_currency):
    try:
        chat_id = message.chat.id
        amount_entered = message.text
        amount_value = helper.validate_entered_amount(amount_entered)  # validate
        amount_value = currencies.convert(selected_currency,'USD',float(amount_value))
        amount_value = str(round(float(amount_value), 2))
        option[selected_category] = amount_value
        print("For {}.{}".format(chat_id, amount_value))
        if amount_value == 0:  # cannot be $0 spending
            raise Exception("Spent amount has to be a non-zero number.")

        date_of_entry = datetime.today().strftime(helper.getDateFormat() + ' ' + helper.getTimeFormat())
        account_str = option[selected_category]
        amount_str = str(amount_value)
        date_str = str(date_of_entry)

        helper.write_json(add_user_record(chat_id, "{},{},Inflow {}".format(date_str, selected_category, amount_str)))
        helper.write_json(update_account_balance_add(chat_id, selected_category, amount_value))
        bot.send_message(chat_id, 'The following expenditure has been recorded: You have Added ${} to {} account on {}'.format(amount_str, account_str, date_str))
        bot.send_message(chat_id, 'New Balance in {} account is: {}'.format(selected_category, helper.get_account_balance(message, bot, selected_category)))
        helper.display_account_balance(message, bot, selected_category)
    except Exception as e:
        logging.exception(str(e))
        bot.reply_to(message, 'Oh no. ' + str(e))

def update_account_balance_add(chat_id, cat, val):
    user_list = helper.read_json()
    if str(chat_id) not in user_list:
        user_list[str(chat_id)] = helper.createNewUserRecord()

    if user_list[str(chat_id)]['balance'][cat] is None:
        user_list[str(chat_id)]['balance'][cat] = str(val)
    else:
        user_list[str(chat_id)]['balance'][cat] = str(float(val) + float(user_list[str(chat_id)]['balance'][cat]))
    return user_list

# Contains step to on user record addition
def add_user_record(chat_id, record_to_be_added):
    user_list = helper.read_json()
    if str(chat_id) not in user_list:
        user_list[str(chat_id)] = helper.createNewUserRecord()

    user_list[str(chat_id)]['balance_data'].append(record_to_be_added)
    return user_list
