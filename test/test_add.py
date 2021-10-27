import sys
import os
import telebot
from telebot import types
from unittest.mock import MagicMock

sys.path.insert(0, os.getcwd() + "/code")
from add import run

bot = telebot.TeleBot("1")
bot.reply_to = MagicMock(return_value=True)
bot.register_next_step_handler = MagicMock(return_value=True)


def test_run():
    message = create_message("hello from test run!")
    ret_msg = run(message, bot)
    assert ret_msg is None


def create_message(text):
    params = {'messagebody': text}
    chat = types.User(11, False, 'test')
    return types.Message(1, None, None, chat, 'text', params, "")


def test_add_user_record():
    pass
