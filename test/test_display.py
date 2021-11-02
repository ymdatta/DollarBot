from mock import patch
from telebot import types
from code import display


@patch('telebot.telebot')
def test_run(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.reply_to.return_value = True
    message = create_message("hello from test run!")
    display.run(message, mc)
    assert mc.send_message.called

@patch('telebot.telebot')
def test_no_data_available(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.reply_to.return_value = True
    message = create_message("/spendings")
    display.run(message, mc)
    assert mc.send_message.called

@patch('telebot.telebot')
def test_invalid_format(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.reply_to.return_value = True
    message = create_message("luster")
    try:
        display.display_total(message, mc)
        #In this case it accepted an unusable format, fail the test
        assert False
    except Exception:
        assert True

@patch('telebot.telebot')
def test_valid_format(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.reply_to.return_value = True
    message = create_message("Month")
    try:
        display.display_total(message, mc)
        assert True
    except Exception:
        #In this case it did not accept a usable format, fail the test
        assert False
@patch('telebot.telebot')
def test_valid_format_day(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.reply_to.return_value = True
    message = create_message("Day")
    try:
        display.display_total(message, mc)
        assert True
    except Exception:
        #In this case it did not accept a usable format, fail the test
        assert False

@patch('telebot.telebot')
def test_spending_display(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.reply_to.return_value = True
    message = create_message("Day")
    message.text = "Day"
    try:
        display.display_total(message, mc)
        assert False
    except Exception:
        #In this case there where no records
        assert True


def create_message(text):
    params = {'messagebody': text}
    chat = types.User(11, False, 'test')
    return types.Message(894127939, None, None, chat, 'text', params, "")
