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
    print("Categories:")
    for c in helper.getSpendCategories():
        print("\t", c)
        markup.add(c)
    msg = bot.reply_to(message, 'Select Category', reply_markup = markup)
    bot.register_next_step_handler(msg, post_category_selection, bot)

# Contains step to run after the category is selected
def post_category_selection(message, bot):
    try:
        chat_id = message.chat.id
        selected_category = message.text
        if selected_category not in helper.getSpendCategories():
            bot.send_message(chat_id, 'Invalid', reply_markup=types.ReplyKeyboardRemove())
            raise Exception("Sorry I don't recognize this category \"{}\"!".format(selected_category))

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

        message = bot.send_message(chat_id, 'How much did you spend on {}? \n(Enter numeric values only)'.format(str(option[chat_id])))
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
        if amount_value == 0:  # cannot be $0 spending
            raise Exception("Spent amount has to be a non-zero number.")

        acc_type = helper.get_account_type(message)
        acc_balance = helper.get_account_balance(message, "", acc_type)

        if is_Valid_expense(message, float(amount_value)) == False:
            raise Exception("Expenses exceed balance in {} account. Current Balance is {}.".format(acc_type, acc_balance))

        helper.write_json(update_balance(message, amount_value))
        date_of_entry = datetime.today().strftime(helper.getDateFormat() + ' ' + helper.getTimeFormat())
        date_str, category_str, amount_str = str(date_of_entry), str(option[chat_id]), str(amount_value)
        helper.write_json(add_user_record(chat_id, "{},{},{},{} Account".format(date_str, category_str, amount_str, acc_type)))
        helper.write_json(add_user_balance_record(chat_id, "{}.{}.Outflow {}".format(date_str, acc_type, amount_value)))
        bot.send_message(chat_id, 'The following expenditure has been recorded: You have spent ${} for {} on {} from {} account'.format(amount_str, category_str, date_str, acc_type))


        if (helper.get_account_balance(message, "", acc_type) < 100):
            bot.send_message(chat_id, 'ALERT: Balance in {} account is less than 100$'.format(acc_type))

        helper.display_remaining_budget(message, bot, selected_category)
    except Exception as e:
        logging.exception(str(e))
        bot.reply_to(message, 'Oh no. ' + str(e))


# By default, we will use checkings account.
# Only if there was a previous configuration of account change to savings, we will use that.
def is_Valid_expense(message, amount):
    acc_type = helper.get_account_type(message)

    if (float(helper.get_account_balance(message, "", acc_type)) < amount):
        return False
    else:
        return True

def update_balance(message, amount):
    cur_balance = float(helper.get_account_balance(message, "", helper.get_account_type(message)))
    cur_balance -= float(amount)

    acc_type = helper.get_account_type(message)

    user_list = helper.read_json()
    user_list[str(message.chat.id)]["balance"][acc_type] = str(cur_balance)
    return user_list

# Contains step to on user record addition
def add_user_record(chat_id, record_to_be_added):
    user_list = helper.read_json()
    if str(chat_id) not in user_list:
        user_list[str(chat_id)] = helper.createNewUserRecord()

    user_list[str(chat_id)]['data'].append(record_to_be_added)
    return user_list

def add_user_balance_record(chat_id, record_to_be_added):
    user_list = helper.read_json()
    if str(chat_id) not in user_list:
        user_list[str(chat_id)] = helper.createNewUserRecord()

    user_list[str(chat_id)]['balance_data'].append(record_to_be_added)
    return user_list
