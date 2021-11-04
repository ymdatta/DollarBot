from code import helper
from code.helper import throw_exception
from mock import ANY
from telebot import types
from mock.mock import patch
import logging
import mock

MOCK_CHAT_ID = 101
MOCK_USER_DATA = {
    str(MOCK_CHAT_ID): {
        'data': ["correct_mock_value"],
        'budget': {
            'overall': None,
            'category': None
        }
    },
    '102': {
        'data': ["wrong_mock_value"],
        'budget': {
            'overall': None,
            'category': None
        }
    }
}


def test_validate_entered_amount_none():
    result = helper.validate_entered_amount(None)
    if result:
        assert False, 'None is not a valid amount'
    else:
        assert True


def test_validate_entered_amount_int():
    val = '101'
    result = helper.validate_entered_amount(val)
    if result:
        assert True
    else:
        assert False, val + ' is valid amount'


def test_validate_entered_amount_int_max():
    val = '999999999999999'
    result = helper.validate_entered_amount(val)
    if result:
        assert True
    else:
        assert False, val + ' is valid amount'


def test_validate_entered_amount_int_outofbound():
    val = '9999999999999999'
    result = helper.validate_entered_amount(val)
    if result:
        assert False, val + ' is not a valid amount(out of bound)'
    else:
        assert True


def test_validate_entered_amount_float():
    val = '101.11'
    result = helper.validate_entered_amount(val)
    if result:
        assert True
    else:
        assert False, val + ' is valid amount'


def test_validate_entered_amount_float_max():
    val = '999999999999999.9999'
    result = helper.validate_entered_amount(val)
    if result:
        assert True
    else:
        assert False, val + ' is valid amount'


def test_validate_entered_amount_float_more_decimal():
    val = '9999999999.999999999'
    result = helper.validate_entered_amount(val)
    if result:
        assert True
    else:
        assert False, val + ' is valid amount'


def test_validate_entered_amount_float_outofbound():
    val = '9999999999999999.99'
    result = helper.validate_entered_amount(val)
    if result:
        assert False, val + ' is not a valid amount(out of bound)'
    else:
        assert True


def test_validate_entered_amount_string():
    val = 'agagahaaaa'
    result = helper.validate_entered_amount(val)
    if result:
        assert False, val + ' is not a valid amount'
    else:
        assert True


def test_validate_entered_amount_string_with_dot():
    val = 'agaga.aaa'
    result = helper.validate_entered_amount(val)
    if result:
        assert False, val + ' is not a valid amount'
    else:
        assert True


def test_validate_entered_amount_special_char():
    val = '$%@*@.@*'
    result = helper.validate_entered_amount(val)
    if result:
        assert False, val + ' is not a valid amount'
    else:
        assert True


def test_validate_entered_amount_alpha_num():
    val = '22e62a'
    result = helper.validate_entered_amount(val)
    if result:
        assert False, val + ' is not a valid amount'
    else:
        assert True


def test_validate_entered_amount_mixed():
    val = 'a14&^%.hs827'
    result = helper.validate_entered_amount(val)
    if result:
        assert False, val + ' is not a valid amount'
    else:
        assert True


def test_getUserHistory_without_data(mocker):
    mocker.patch.object(helper, 'read_json')
    helper.read_json.return_value = {}
    result = helper.getUserHistory(MOCK_CHAT_ID)
    if result is None:
        assert True
    else:
        assert False, 'Result is not None when user data does not exist'


def test_getUserHistory_with_data(mocker):
    mocker.patch.object(helper, 'read_json')
    helper.read_json.return_value = MOCK_USER_DATA
    result = helper.getUserHistory(MOCK_CHAT_ID)
    if result == MOCK_USER_DATA[str(MOCK_CHAT_ID)]['data']:
        assert True
    else:
        assert False, 'User data is available but not found'


def test_getUserHistory_with_none(mocker):
    mocker.patch.object(helper, 'read_json')
    helper.read_json.return_value = None
    result = helper.getUserHistory(MOCK_CHAT_ID)
    if result is None:
        assert True
    else:
        assert False, 'Result is not None when the file does not exist'


def test_getSpendCategories():
    result = helper.getSpendCategories()
    if result == helper.spend_categories:
        assert True
    else:
        assert False, 'expected spend categories are not returned'


def test_getSpendDisplayOptions():
    result = helper.getSpendDisplayOptions()
    if result == helper.spend_display_option:
        assert True
    else:
        assert False, 'expected spend display options are not returned'


def test_getCommands():
    result = helper.getCommands()
    if result == helper.commands:
        assert True
    else:
        assert False, 'expected commands are not returned'


def test_getDateFormat():
    result = helper.getDateFormat()
    if result == helper.dateFormat:
        assert True
    else:
        assert False, 'expected date format are not returned'


def test_getTimeFormat():
    result = helper.getTimeFormat()
    if result == helper.timeFormat:
        assert True
    else:
        assert False, 'expected time format are not returned'


def test_getMonthFormat():
    result = helper.getMonthFormat()
    if result == helper.monthFormat:
        assert True
    else:
        assert False, 'expected month format are not returned'


def test_getChoices():
    result = helper.getChoices()
    if result == helper.choices:
        assert True
    else:
        assert False, 'expected choices are not returned'


def test_write_json(mocker):
    mocker.patch.object(helper, 'json')
    helper.json.dump.return_value = True
    user_list = ['hello']
    helper.write_json(user_list)
    helper.json.dump.assert_called_with(user_list, ANY, ensure_ascii=ANY, indent=ANY)


@patch('telebot.telebot')
def test_throw_exception(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.reply_to.return_value = True

    message = create_message("message from testing")

    throw_exception("hello, exception from testing", message, mc, logging)
    mc.reply_to.assert_called_with(message, 'Oh no! hello, exception from testing')


def test_createNewUserRecord():
    data_format_call = helper.createNewUserRecord()
    data_format = {
        'data': [],
        'budget': {
            'overall': None,
            'category': None
        }
    }
    assert(sorted(data_format_call) == sorted(data_format))


def test_getOverallBudget_none_case():
    helper.getUserData.return_value = None
    overall_budget = helper.getOverallBudget(11)
    assert(overall_budget is None)


def test_getOverallBudget_working_case():
    helper.getUserData = mock.Mock(return_value={'budget': {'overall': 10}})
    overall_budget = helper.getOverallBudget(11)
    assert(overall_budget == 10)


def test_getCategoryBudget_none_case():
    helper.getUserData.return_value = None
    overall_budget = helper.getCategoryBudget(11)
    assert(overall_budget is None)


def test_getCategoryBudget_working_case():
    helper.getUserData = mock.Mock(return_value={'budget': {'category': {'Food': 10}}})
    overall_budget = helper.getCategoryBudget(11)
    assert(overall_budget is not None)


def test_getCategoryBudgetByCategory():
    pass


def create_message(text):
    params = {'messagebody': text}
    chat = types.User(11, False, 'test')
    return types.Message(1, None, None, chat, 'text', params, "")
