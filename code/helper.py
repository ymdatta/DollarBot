import re
import json
import os
from datetime import datetime

spend_categories = ['Food', 'Groceries', 'Utilities', 'Transport', 'Shopping', 'Miscellaneous']
choices = ['Date', 'Category', 'Cost']
spend_display_option = ['Day', 'Month']

update_options = {
    'continue': 'Continue',
    'exit': 'Exit'
}

budget_options = {
    'update': 'Add/Update',
    'view': 'View',
    'delete': 'Delete'
}

budget_types = {
    'overall': 'Overall Budget',
    'category': 'Category-Wise Budget'
}

data_format = {
    'data': [],
    'budget': {
        'overall': None,
        'category': None
    }
}

# set of implemented commands and their description
commands = {
    'menu': 'Display this menu',
    'add': 'Record/Add a new spending',
    'display': 'Show sum of expenditure for the current day/month',
    'history': 'Display spending history',
    'delete': 'Clear/Erase all your records',
    'edit': 'Edit/Change spending details',
    'budget': 'Add/Update/View/Delete budget'
}

dateFormat = '%d-%b-%Y'
timeFormat = '%H:%M'
monthFormat = '%b-%Y'


# function to load .json expense record data
def read_json():
    try:
        if not os.path.exists('expense_record.json'):
            with open('expense_record.json', 'w') as json_file:
                json_file.write('{}')
            return json.dumps('{}')
        elif os.stat('expense_record.json').st_size != 0:
            with open('expense_record.json') as expense_record:
                expense_record_data = json.load(expense_record)
            return expense_record_data

    except FileNotFoundError:
        print("---------NO RECORDS FOUND---------")


def write_json(user_list):
    try:
        with open('expense_record.json', 'w') as json_file:
            json.dump(user_list, json_file, ensure_ascii=False, indent=4)
    except FileNotFoundError:
        print('Sorry, the data file could not be found.')


def validate_entered_amount(amount_entered):
    if len(amount_entered) > 0 and len(amount_entered) <= 15:
        if amount_entered.isdigit:
            if re.match("^[0-9]*\\.?[0-9]*$", amount_entered):
                amount = round(float(amount_entered), 2)
                if amount > 0:
                    return str(amount)
    return 0


def getUserHistory(chat_id):
    data = getUserData(chat_id)
    if data is not None:
        return data['data']
    return None


def getUserData(chat_id):
    user_list = read_json()
    if (str(chat_id) in user_list):
        return user_list[str(chat_id)]
    return None


def throw_exception(e, message, bot, logging):
    logging.exception(str(e))
    bot.reply_to(message, 'Oh no! ' + str(e))


def createNewUserRecord():
    return data_format


def getOverallBudget(chatId):
    data = getUserData(chatId)
    if data is None:
        return None
    return data['budget']['overall']


def getCategoryBudget(chatId):
    data = getUserData(chatId)
    if data is None:
        return None
    return data['budget']['category']


def getCategoryBudgetByCategory(chatId, cat):
    if not isCategoryBudgetByCategoryAvailable(chatId, cat):
        return None
    data = getCategoryBudget(chatId)
    return data[cat]


def canAddBudget(chatId):
    return (getOverallBudget(chatId) is None) and (getCategoryBudget(chatId) is None)


def isOverallBudgetAvailable(chatId):
    return getOverallBudget(chatId) is not None


def isCategoryBudgetAvailable(chatId):
    return getCategoryBudget(chatId) is not None


def isCategoryBudgetByCategoryAvailable(chatId, cat):
    data = getCategoryBudget(chatId)
    if data is None:
        return False
    return cat in data.keys()


def display_remaining_budget(message, bot, cat):
    chat_id = message.chat.id
    if isOverallBudgetAvailable(chat_id):
        display_remaining_overall_budget(message, bot)
    elif isCategoryBudgetByCategoryAvailable(chat_id, cat):
        display_remaining_category_budget(message, bot, cat)


def display_remaining_overall_budget(message, bot):
    chat_id = message.chat.id
    remaining_budget = calculateRemainingOverallBudget(chat_id)
    if remaining_budget >= 0:
        msg = '\nRemaining Overall Budget is $' + str(remaining_budget)
    else:
        msg = '\nBudget Exceded!\nExpenditure exceeds the budget by $' + str(remaining_budget)[1:]
    bot.send_message(chat_id, msg)


def calculateRemainingOverallBudget(chat_id):
    budget = getOverallBudget(chat_id)
    history = getUserHistory(chat_id)
    query = datetime.now().today().strftime(getMonthFormat())
    queryResult = [value for index, value in enumerate(history) if str(query) in value]

    return float(budget) - calculate_total_spendings(queryResult)


def calculate_total_spendings(queryResult):
    total = 0
    total_dict = {}

    for row in queryResult:
        s = row.split(',')
        total = total + float(s[2])
    return total


def display_remaining_category_budget(message, bot, cat):
    chat_id = message.chat.id
    remaining_budget = calculateRemainingCategoryBudget(chat_id, cat)
    if remaining_budget >= 0:
        msg = '\nRemaining Budget for ' + cat + ' is $' + str(remaining_budget)
    else:
        msg = '\nBudget for ' + cat + ' Exceded!\nExpenditure exceeds the budget by $' + str(abs(remaining_budget))
    bot.send_message(chat_id, msg)


def calculateRemainingCategoryBudget(chat_id, cat):
    budget = getCategoryBudgetByCategory(chat_id, cat)
    history = getUserHistory(chat_id)
    query = datetime.now().today().strftime(getMonthFormat())
    queryResult = [value for index, value in enumerate(history) if str(query) in value]

    return float(budget) - calculate_total_spendings_for_category(queryResult, cat)


def calculate_total_spendings_for_category(queryResult, cat):
    total = 0
    total_dict = {}

    for row in queryResult:
        s = row.split(',')
        if cat == s[1]:
            total = total + float(s[2])
    return total


def getSpendCategories():
    return spend_categories


def getSpendDisplayOptions():
    return spend_display_option


def getCommands():
    return commands


def getDateFormat():
    return dateFormat


def getTimeFormat():
    return timeFormat


def getMonthFormat():
    return monthFormat


def getChoices():
    return choices


def getBudgetOptions():
    return budget_options


def getBudgetTypes():
    return budget_types


def getUpdateOptions():
    return update_options
