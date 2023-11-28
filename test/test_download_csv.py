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
