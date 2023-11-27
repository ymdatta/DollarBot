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
from forex_python.converter import CurrencyRates

currencies = CurrencyRates(force_decimal = False)

def run(message, bot):
    chat_id = message.chat.id
    if (not (helper.isOverallBudgetAvailable(chat_id)) and (helper.isCategoryBudgetAvailable(chat_id))):
        update_overall_budget(message, bot)
    elif (not (helper.isCategoryBudgetAvailable(chat_id)) and (helper.isOverallBudgetAvailable(chat_id))):
        update_category_budget(message, bot)
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        options = helper.getBudgetTypes()
        markup.row_width = 2
        for c in options.values():
            markup.add(c)
        msg = bot.reply_to(message, 'Select Budget Type', reply_markup=markup)
        bot.register_next_step_handler(msg, post_type_selection, bot)

def post_type_selection(message, bot):
    try:
        chat_id = message.chat.id
        op = message.text
        options = helper.getBudgetTypes()
        if op not in options.values():
            bot.send_message(chat_id, 'Invalid', reply_markup=types.ReplyKeyboardRemove())
            raise Exception("Sorry I don't recognise this operation \"{}\"!".format(op))
        if op == options['overall']:
            update_overall_budget(message, bot)
        elif op == options['category']:
            update_category_budget(message, bot)
    except Exception as e:
        helper.throw_exception(e, message, bot, logging)

def update_overall_budget(message, bot):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    curr = helper.getCurrencies()
    markup.row_width = 2
    for c in curr:
        markup.add(c)
    msg = bot.reply_to(message, 'Select Currency', reply_markup=markup)
    print('currency = ' + msg.text)
    bot.register_next_step_handler(msg, post_currency_selection, bot)

def post_currency_selection(message, bot):
    try:
        chat_id = message.chat.id
        selected_currency = message.text
        if selected_currency not in helper.getCurrencies():
            bot.send_message(chat_id, 'Invalid', reply_markup=types.ReplyKeyboardRemove())
            raise Exception("Sorry I don't recognize this currency \"{}\"!".format(selected_currency))
        if (helper.isOverallBudgetAvailable(chat_id)):
            currentBudget = helper.getOverallBudget(chat_id)
            msg_string = 'Current Budget is ${}\n\nHow much is your new monthly budget? \n(Enter numeric values only)'
            msg = bot.send_message(chat_id, msg_string.format(currentBudget))
        else:
            msg = bot.send_message(chat_id, 'How much is your monthly budget? \n(Enter numeric values only)')
        bot.register_next_step_handler(msg, post_overall_amount_input, bot, selected_currency)
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

def post_overall_amount_input(message, bot, selected_currency):
    try:
        chat_id = message.chat.id
        amount_value = helper.validate_entered_amount(message.text)
        amount_value = currencies.convert(selected_currency,'USD',float(amount_value))
        amount_value = str(round(float(amount_value), 2))
        if amount_value == 0:
            raise Exception("Invalid amount.")
        user_list = helper.read_json()
        if str(chat_id) not in user_list:
            user_list[str(chat_id)] = helper.createNewUserRecord()
        user_list[str(chat_id)]['budget']['overall'] = amount_value
        helper.write_json(user_list)
        bot.send_message(chat_id, 'Budget Updated!')
        return user_list
    except Exception as e:
        helper.throw_exception(e, message, bot, logging)


def update_category_budget(message, bot):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    categories = helper.getSpendCategories()
    markup.row_width = 2
    for c in categories:
        markup.add(c)
    msg = bot.reply_to(message, 'Select Category', reply_markup=markup)
    print('category = ' + msg.text)
    bot.register_next_step_handler(msg, post_category_selection, bot)


def post_category_selection(message, bot):
    try:
        chat_id = message.chat.id
        selected_category = message.text
        categories = helper.getSpendCategories()
        if selected_category not in categories:
            bot.send_message(chat_id, 'Invalid', reply_markup=types.ReplyKeyboardRemove())
            raise Exception("Sorry I don't recognise this category \"{}\"!".format(selected_category))
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row_width = 2
        print("Currencies:")
        for c in helper.getCurrencies():
            print("\t", c)
            markup.add(c)
        msg = bot.reply_to(message, 'Select Currency', reply_markup=markup)
        print('category = ' + selected_category)
        bot.register_next_step_handler(msg, post_currency_selection_for_category_update, bot, selected_category)
    except Exception as e:
        helper.throw_exception(e, message, bot, logging)

def post_currency_selection_for_category_update(message, bot, selected_category):
    try:
        chat_id = message.chat.id
        # selected_category = message.text
        # curr = helper.getCurrencies()
        selected_currency = message.text
        print('currency = ' + selected_currency)
        if selected_currency not in helper.getCurrencies():
            bot.send_message(chat_id, 'Invalid', reply_markup=types.ReplyKeyboardRemove())
            raise Exception("Sorry I don't recognise this currency \"{}\"!".format(selected_currency))
        if helper.isCategoryBudgetByCategoryAvailable(chat_id, selected_category):
            currentBudget = helper.getCategoryBudgetByCategory(chat_id, selected_category)
            msg_string = 'Current monthly budget for {} is {}\n\nEnter monthly budget for {}\n(Enter numeric values only)'
            message = bot.send_message(chat_id, msg_string.format(selected_category, currentBudget, selected_category))
        else:
            message = bot.send_message(chat_id, 'Enter monthly budget for ' + selected_category + '\n(Enter numeric values only)')
        bot.register_next_step_handler(message, post_category_amount_input, bot, selected_category, selected_currency)
    except Exception as e:
        helper.throw_exception(e, message, bot, logging)

def post_category_amount_input(message, bot, category, currency):
    try:
        chat_id = message.chat.id
        amount_value = helper.validate_entered_amount(message.text)
        amount_value = currencies.convert(currency,'USD',float(amount_value))
        amount_value = str(round(float(amount_value), 2))
        if amount_value == 0:
            raise Exception("Invalid amount.")
        user_list = helper.read_json()
        if str(chat_id) not in user_list:
            user_list[str(chat_id)] = helper.createNewUserRecord()
        if user_list[str(chat_id)]['budget']['category'] is None:
            user_list[str(chat_id)]['budget']['category'] = {}
        user_list[str(chat_id)]['budget']['category'][category] = amount_value
        helper.write_json(user_list)
        message = bot.send_message(chat_id, 'Budget for ' + category + ' Created!')
        post_category_add(message, bot)

    except Exception as e:
        helper.throw_exception(e, message, bot, logging)


def post_category_add(message, bot):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = helper.getUpdateOptions().values()
    markup.row_width = 2
    for c in options:
        markup.add(c)
    msg = bot.reply_to(message, 'Select Option', reply_markup=markup)
    bot.register_next_step_handler(msg, post_option_selection, bot)


def post_option_selection(message, bot):
    print("here")
    selected_option = message.text
    options = helper.getUpdateOptions()
    print("here")
    if selected_option == options['continue']:
        update_category_budget(message, bot)
