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
import matplotlib.pyplot as plt

def run(message, bot):
    try:
        helper.read_json()
        chat_id = message.chat.id
        user_history = helper.getUserHistory(chat_id)
        spend_total_str = ""
        # Amount for each month
        amount = 0.0
        am = ""
        Dict = {'Jan': 0.0, 'Feb': 0.0, 'Mar': 0.0, 'Apr': 0.0, 'May': 0.0, 'Jun': 0.0, 'Jul': 0.0, 'Sep': 0.0, 'Oct': 0.0, 'Nov': 0.0, 'Dec': 0.0}
        if user_history is None:
            raise Exception("Sorry! No spending records found!")
        spend_total_str = "Here is your spending history : \nDATE, CATEGORY, AMOUNT\n----------------------\n"
        if len(user_history) == 0:
            spend_total_str = "Sorry! No spending records found!"
        else:
            for rec in user_history:
                spend_total_str += str(rec) + "\n"
                av = str(rec).split(",")
                ax = av[0].split("-")
                am = ax[1]
                amount = Dict[am] + float(av[2])
                Dict[am] = amount
        bot.send_message(chat_id, spend_total_str)

        # bot.send_message(chat_id, Dict[am])
        plt.clf()
        width = 1.0
        plt.bar(Dict.keys(), Dict.values(), width, color='g')
        plt.savefig('histo.png')
        bot.send_photo(chat_id, photo=open('histo.png', 'rb'))
        ##bot.send_message(chat_id, amount)
    except Exception as e:
        logging.exception(str(e))
        bot.reply_to(message, "Oops!" + str(e))
