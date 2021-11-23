import helper
import logging
from telebot import types

def run(message, bot):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = helper.getCategoryOptions()
    markup.row_width = 2
    for c in options.values():
        markup.add(c)
    msg = bot.reply_to(message, 'Select Operation', reply_markup=markup)
    bot.register_next_step_handler(msg, post_operation_selection, bot)
    
def post_operation_selection(message, bot):
    try:
        chat_id = message.chat.id
        op = message.text
        options = helper.getCategoryOptions()
        if op not in options.values():
            bot.send_message(chat_id, 'Invalid', reply_markup=types.ReplyKeyboardRemove())
            raise Exception("Sorry I don't recognise this operation \"{}\"!".format(op))
        if op == options['add']:
            msg = bot.reply_to(message, 'Please type the new category name')
            bot.register_next_step_handler(msg, category_add, bot)
        #elif op == options['view']:
        #    category_view.run(message, bot)
        #elif op == options['delete']:
        #    category_delete.run(message, bot)
    except Exception as e:
        # print("hit exception")
        helper.throw_exception(e, message, bot, logging)
    
    
def category_add(message, bot):
    chat_id = message.chat.id
    category_name = message.text
    with open("categories.txt", "r") as tf:
        lines = tf.read().split(',')
        tf.close()
    f = open("categories.txt", "a")   
    if lines == ['']:
        f.write(category_name)    
    else:
        f.write("," + category_name)
    f.close()
    bot.send_message(chat_id, 'Add category "{}" successfully!'.format(category_name))
    