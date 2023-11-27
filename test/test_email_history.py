import smtplib
import unittest
from unittest.mock import patch, Mock, mock_open, call
import tempfile
from code import email_history
import os
from mock import mock_open, patch

@patch('code.email_history.smtplib.SMTP')
def test_send_email_successful(mock_smtp):
    mock_server = Mock()
    mock_smtp.return_value = mock_server

    recipient_email = "example@example.com"
    email_subject = "Test Subject"
    email_body = "Test Message"
    attachment_path = 'test_attachment.txt'

    with open('test_attachment.txt', 'w') as dummy_file:
        dummy_file.write("This is a test attachment.")

    try:
        email_history.send_email(mock_server, recipient_email, email_subject, email_body, attachment_path)

        mock_server.sendmail.assert_called_once_with("dollarbotnoreply@gmail.com", recipient_email, mock_server.sendmail.call_args[0][2])
    finally:
        os.remove('test_attachment.txt')


@patch('code.email_history.smtplib.SMTP')
def test_send_email_failure(mock_smtp):
    mock_server = Mock()
    mock_smtp.return_value = mock_server

    recipient_email = "example@example.com"
    email_subject = "Test Subject"
    email_body = "Test Message"
    attachment_path = 'test_attachment.txt'

    with open('test_attachment.txt', 'w') as dummy_file:
        dummy_file.write("This is a test attachment.")

    try:
        email_history.send_email(mock_server, recipient_email, email_subject, email_body, attachment_path)

        mock_server.sendmail.assert_called_once_with("dollarbotnoreply@gmail.com", recipient_email, mock_server.sendmail.call_args[0][2])
    finally:
        os.remove('test_attachment.txt')


@patch('code.email_history.smtplib.SMTP')
def test_close_smtp_connection_successful(mock_smtp):
    smtp_server = Mock()
    email_history.close_smtp_connection(smtp_server)
    smtp_server.quit.assert_called_once()

@patch('smtplib.SMTP')
@patch('code.email_history.logging')
def test_connect_to_smtp_server_success(mock_logging, mock_smtp):
    # Arrange
    smtp_instance = mock_smtp.return_value

    # Act
    result = email_history.connect_to_smtp_server()

    # Assert
    smtp_instance.starttls.assert_called_once()
    smtp_instance.login.assert_called_once_with("dollarbotnoreply@gmail.com", "ogrigybfufihnkcc")
    mock_logging.info.assert_called_with("Successfully connected to the SMTP server")
    assert result == smtp_instance

@patch('smtplib.SMTP')
@patch('code.email_history.logging')
def test_connect_to_smtp_server_failure(mock_logging, mock_smtp):

    mock_smtp.side_effect = smtplib.SMTPException('Test SMTPException')

    # Act/Assert
    with unittest.TestCase().assertRaises(smtplib.SMTPException) as context:
        email_history.connect_to_smtp_server()

    mock_logging.error.assert_called_with('SMTP Exception: Test SMTPException')
    assert str(context.exception) == 'Test SMTPException'

if __name__ == '__main__':
    unittest.main()
