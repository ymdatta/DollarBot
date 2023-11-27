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


def run(message, bot):
    try:
        print("here")
        chat_id = message.chat.id
        if helper.isOverallBudgetAvailable(chat_id):
            display_overall_budget(message, bot)
        elif helper.isCategoryBudgetAvailable(chat_id):
            display_category_budget(message, bot)
        else:
            raise Exception('Budget does not exist. Use ' + helper.getBudgetOptions()['update'] + ' option to add/update the budget')
    except Exception as e:
        helper.throw_exception(e, message, bot, logging)


def display_overall_budget(message, bot):
    chat_id = message.chat.id
    data = helper.getOverallBudget(chat_id)
    bot.send_message(chat_id, 'Overall Budget: $' + data)


def display_category_budget(message, bot):
    chat_id = message.chat.id
    data = helper.getCategoryBudget(chat_id)
    res = "Budget Summary\n"
    for c, v in data.items():
        res = res + c + ": $" + v + "\n"
    bot.send_message(chat_id, res)
