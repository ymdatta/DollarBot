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


def run(message, bot):
    global user_list
    chat_id = message.chat.id
    delete_history_text = ""
    user_list = helper.read_json()
    if (str(chat_id) in user_list):
        helper.write_json(deleteHistory(chat_id))
        delete_history_text = "History has been deleted!"
    else:
        delete_history_text = "No records there to be deleted. Start adding your expenses to keep track of your spendings!"
    bot.send_message(chat_id, delete_history_text)


# function to delete a record
def deleteHistory(chat_id):
    global user_list
    if (str(chat_id) in user_list):
        del user_list[str(chat_id)]
    return user_list
