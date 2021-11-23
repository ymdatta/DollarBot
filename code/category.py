import helper
from telebot import types

def run(message, bot):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    msg = bot.reply_to(message, 'Type the new Category name', reply_markup=markup)
    bot.register_next_step_handler(msg, post_category_adding, bot)
    
def post_category_adding(message, bot):
    chat_id = message.chat.id
    category_name = message.text
    
    with open("categories.txt", "r") as tf:
        lines = tf.read().split(',')
        tf.close()
    
    print(len(lines))
    print(lines)
    print(type(lines))
    
    f = open("categories.txt", "a")   
    if lines == ['']:
        f.write(category_name)    
    else:
        f.write("," + category_name)
    f.close()
    
    bot.send_message(chat_id, 'Add category "{}" successfully!'.format(category_name))