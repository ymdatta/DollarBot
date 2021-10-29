from mock.mock import patch
from telebot import types
from code import add


@patch('telebot.telebot')
def test_run(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.reply_to.return_value = True
    message = create_message("hello from test run!")
    add.run(message, mc)
    assert(mc.reply_to.called)


@patch('telebot.telebot')
def test_post_category_selection_working(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.send_message.return_value = True

    message = create_message("hello from testing!")
    add.post_category_selection(message, mc)
    assert(mc.send_message.called)


@patch('telebot.telebot')
def test_post_category_selection_noMatchingCategory(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.send_message.return_value = []
    mc.reply_to.return_value = True

    mocker.patch.object(add, 'helper')
    add.helper.getSpendCategories.return_value = None

    message = create_message("hello from testing!")
    add.post_category_selection(message, mc)
    assert(mc.reply_to.called)


@patch('telebot.telebot')
def test_post_amount_input_working(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.send_message.return_value = True

    message = create_message("hello from testing!")
    add.post_category_selection(message, mc)
    assert(mc.send_message.called)


@patch('telebot.telebot')
def test_post_amount_input_nonworking(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.send_message.return_value = True
    mc.reply_to.return_value = True
    mocker.patch.object(add, 'helper')
    add.helper.validate_entered_amount.return_value = 0

    message = create_message("hello from testing!")
    add.post_category_selection(message, mc)
    assert(mc.reply_to.called)


def test_add_user_record(mocker):
    mocker.patch.object(add, 'helper')
    add.helper.read_json.return_value = {}

    addeduserrecord = add.add_user_record(1, "record : test")
    print(addeduserrecord)
    assert(addeduserrecord)


def create_message(text):
    params = {'messagebody': text}
    chat = types.User(11, False, 'test')
    return types.Message(1, None, None, chat, 'text', params, "")
