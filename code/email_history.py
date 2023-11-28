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

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os.path
import threading
import extract

# Constants and Configurations
SMTP_PORT = 587
SMTP_SERVER = "smtp.gmail.com"
SENDER_EMAIL = "dollarbotnoreply@gmail.com"
SENDER_PASSWORD = "ogrigybfufihnkcc"

extract_complete = threading.Event()

def connect_to_smtp_server():
    """
    Connect to the SMTP server using the provided credentials.

    Returns:
        smtplib.SMTP: Connected SMTP server.
    """
    try:
        logging.info("Connecting to SMTP server...")
        smtp_server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp_server.starttls()
        smtp_server.login(SENDER_EMAIL, SENDER_PASSWORD)
        logging.info("Successfully connected to the SMTP server")
        return smtp_server
    except smtplib.SMTPException as e:
        logging.error(f"SMTP Exception: {str(e)}")
        raise

def send_email(smtp_server, recipient_email, email_subject, email_body, attachment_path):
    """
    Send an email with an attachment.

    Args:
        smtp_server (smtplib.SMTP): Connected SMTP server.
        recipient_email (str): Email address of the recipient.
        email_subject (str): Subject of the email.
        email_body (str): Body of the email.
        attachment_path (str): Path to the attachment file.
    """
    try:
        body = email_body
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = email_subject

        msg.attach(MIMEText(body, 'plain'))

        attachment_filename = attachment_path

        with open(attachment_filename, 'rb') as attachment_file:
            attachment_package = MIMEBase('application', 'octet-stream')
            attachment_package.set_payload(attachment_file.read())
            encoders.encode_base64(attachment_package)
            attachment_package.add_header('Content-Disposition', "attachment; filename= " + attachment_filename)
            msg.attach(attachment_package)

        email_text = msg.as_string()

        logging.info(f"Sending email to: {recipient_email}...")
        smtp_server.sendmail(SENDER_EMAIL, recipient_email, email_text)
        logging.info(f"Email sent to: {recipient_email}")

    except IOError as e:
        logging.error(f"IOError: {str(e)}")
        raise
    except smtplib.SMTPRecipientsRefused as e:
        logging.error(f"SMTP Recipients Refused: {str(e)}")
        raise
    except smtplib.SMTPSenderRefused as e:
        logging.error(f"SMTP Sender Refused: {str(e)}")
        raise
    except smtplib.SMTPException as e:
        logging.error(f"SMTP Exception: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        raise

def close_smtp_connection(smtp_server):
    """
    Close the connection to the SMTP server.

    Args:
        smtp_server (smtplib.SMTP): Connected SMTP server.
    """
    try:
        smtp_server.quit()
    except Exception as e:
        logging.error(f"Error while closing SMTP connection: {str(e)}")
        raise

def run(message, bot):
    """
    Run the main process for handling user input.

    Args:
        message: User input message.
        bot: Telegram bot instance.
    """
    try:
        chat_id = message.chat.id
        message = bot.send_message(chat_id, 'Enter the email address to which you want to send your spend history')
        bot.register_next_step_handler(message, handle_email_input, bot)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

def handle_email_input(message, bot):
    """
    Handle user input for the email address and initiate the email sending process.

    Args:
        message: User input message.
        bot: Telegram bot instance.
    """
    try:
        chat_id = message.chat.id
        user_email = message.text

        email_subject = "Your DollarBot Spend History"
        email_body = f"Hello {user_email},\n\nPlease find the attachment of your spend history"

        file_exist = os.path.isfile('code/Expenses_Data.csv')
        if file_exist:
            smtp_server = connect_to_smtp_server()
            send_email(smtp_server, user_email, email_subject, email_body, 'code/Expenses_Data.csv')
        else:
            file_path = extract.run(message, bot)
            smtp_server = connect_to_smtp_server()
            send_email(smtp_server, user_email, email_subject, email_body, file_path)

        close_smtp_connection(smtp_server)
        message = bot.send_message(chat_id, 'Your Email has been sent successfully!')

    except extract.ExtractError as e:
        logging.error(f"Error during data extraction: {str(e)}")
        message = bot.send_message(chat_id, 'Error during data extraction. Please try again.')
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise