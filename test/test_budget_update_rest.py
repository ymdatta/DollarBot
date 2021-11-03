from code import budget_update
from mock import ANY
from mock.mock import patch
from telebot import types


@patch('telebot.telebot')
def test_update_overall_budget_already_available_case(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.send_message.return_value = True

    mocker.patch.object(budget_update, 'helper')
    budget_update.helper.isOverallBudgetAvailable.return_value = True
    budget_update.helper.getOverallBudget.return_value = 100

    budget_update.update_overall_budget(120, mc)
    mc.send_message.assert_called_with(120, ANY)


def create_message(text):
    params = {'messagebody': text}
    chat = types.User(11, False, 'test')
    message = types.Message(1, None, None, chat, 'text', params, "")
    message.text = text
    return message
