from mock import ANY
from mock.mock import patch
from telebot import types
from code import budget


@patch('telebot.telebot')
def test_run(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.reply_to.return_value = True
    message = create_message("hello from test run!")
    budget.run(message, mc)
    assert(mc.reply_to.called_with(ANY, 'Select Operation', ANY))


@patch('telebot.telebot')
def test_post_operation_selection_failing_case(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.send_message.return_value = True

    mocker.patch.object(budget, 'helper')
    budget.helper.getBudgetOptions.return_value = {}

    message = create_message("hello from budget test run!")
    budget.post_operation_selection(message, mc)
    assert(mc.send_message.called_with(11, 'Invalid', ANY))


def create_message(text):
    params = {'messagebody': text}
    chat = types.User(11, False, 'test')
    message = types.Message(1, None, None, chat, 'text', params, "")
    message.text = text
    return message
