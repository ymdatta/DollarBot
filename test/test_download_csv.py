import unittest
from unittest.mock import MagicMock, patch
from code import download_csv

@patch('code.download_csv.helper.getUserHistory', return_value=[['2023-01-01', 'Food', '20', 'Credit']])
@patch('telebot.telebot')
def test_run_successful(mock_bot, mock_get_user_history):
    message = MagicMock()
    result = download_csv.run(message, mock_bot)
    
    mock_bot.send_document.assert_called_once()
    mock_get_user_history.assert_called_once()

@patch('code.download_csv.helper.getUserHistory', return_value=None)
@patch('telebot.telebot')
def test_run_no_history(mock_bot, mock_get_user_history):
    message = MagicMock()
    result = download_csv.run(message, mock_bot)
    
    assert result is None
    mock_bot.send_message.assert_called_once()
    mock_get_user_history.assert_called_once()

@patch('code.download_csv.helper.getUserHistory', side_effect=FileNotFoundError("File not found"))
@patch('telebot.telebot')
def test_run_file_not_found_error(mock_bot, mock_get_user_history):
    message = MagicMock() 
    result = download_csv.run(message, mock_bot)
    
    assert result is None
    mock_bot.send_message.assert_called_once()
    mock_get_user_history.assert_called_once()

if __name__ == '__main__':
    unittest.main()
