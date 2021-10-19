import re
import helper
from telebot import types


def run(m, bot):
    helper.read_json()
    global user_list
    chat_id = m.chat.id

    if (str(chat_id) in user_list):
        info = bot.reply_to(m, "Please enter the date and category of the transaction you made (Eg: 01-Mar-2021,Transport)")
        bot.register_next_step_handler(info, edit2, bot)
    else:
        bot.reply_to(chat_id, "No data found")


i_edit = -1


def edit2(m, bot):
    global i_edit
    i_edit = -1
    chat_id = m.chat.id
    data_edit = helper.getUserHistory(chat_id)
    info = m.text
    date_format = "^(([0][1-9])|([1-2][0-9])|([3][0-1]))\-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\-\d{4}$"
    info = info.split(',')
    x = re.search(date_format, info[0])
    if(x is None):
        bot.reply_to(m, "The date is incorrect")
        return

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    choices = ['Date', 'Category', 'Cost']
    for c in choices:
        markup.add(c)

    for record in data_edit:
        i_edit = i_edit + 1
        record = record.split(',')
        if info[0] == record[0][0:11] and info[1] == record[1]:
            choice = bot.reply_to(m, "What do you want to update?", reply_markup=markup)
            bot.register_next_step_handler(choice, edit3)
            break


def edit3(m, bot):
    choice1 = m.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    for cat in helper.getSpendCategories():
        markup.add(cat)

    if(choice1 == 'Date'):
        new_date = bot.reply_to(m, "Please enter the new date (in dd-mmm-yyy format)")
        bot.register_next_step_handler(new_date, edit_date)

    if(choice1 == 'Category'):
        new_cat = bot.reply_to(m, "Please select the new category", reply_markup=markup)
        bot.register_next_step_handler(new_cat, edit_cat)

    if(choice1 == 'Cost'):
        new_cost = bot.reply_to(m, "Please type the new cost")
        bot.register_next_step_handler(new_cost, edit_cost)


def edit_date(m, bot):
    global i_edit
    new_date = m.text
    date_format = "^(([0][1-9])|([1-2][0-9])|([3][0-1]))\-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\-\d{4}$"
    chat_id = m.chat.id
    data_edit = helper.getUserHistory(chat_id)
    x1 = re.search(date_format, new_date)
    if(x1 is None):
        bot.reply_to(m, "The date is incorrect")
        return
    record = data_edit[i_edit].split(',')
    record[0] = new_date + record[0][11:len(record[0])]
    data_edit[i_edit] = record[0] + ',' + record[1] + ',' + record[2]
    user_list[str(chat_id)] = data_edit
    helper.write_json(user_list)
    bot.reply_to(m, "Date is updated")


def edit_cat(m, bot):
    global i_edit
    chat_id = m.chat.id
    data_edit = helper.getUserHistory(chat_id)
    new_cat = m.text
    record = data_edit[i_edit].split(',')
    record[1] = new_cat
    data_edit[i_edit] = record[0] + ',' + record[1] + ',' + record[2]
    user_list[str(chat_id)] = data_edit
    helper.write_json(user_list)
    bot.reply_to(m, "Category is updated")


def edit_cost(m, bot):
    global i_edit
    new_cost = m.text
    chat_id = m.chat.id
    data_edit = helper.getUserHistory(chat_id)

    if(helper.validate_entered_amount(new_cost) != 0):
        record = data_edit[i_edit].split(',')
        record[2] = new_cost
        data_edit[i_edit] = record[0] + ',' + record[1] + ',' + str(float(record[2]))
        user_list[str(chat_id)] = data_edit
        helper.write_json(user_list)
        bot.reply_to(m, "Cost is updated")
    else:
        bot.reply_to(m, "The cost is invalid")
        return
