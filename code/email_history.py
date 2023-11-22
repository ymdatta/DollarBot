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
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        raise

def close_smtp_connection(smtp_server):
    try:
        smtp_server.quit()
    except Exception as e:
        logging.error(f"Error while closing SMTP connection: {str(e)}")
        raise

def run(message, bot):
    try:
        chat_id = message.chat.id
        message = bot.send_message(chat_id, 'Enter the email address to which you want to send your spend history')
        bot.register_next_step_handler(message, handle_email_input, bot)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

def handle_email_input(message, bot):
    try:
        chat_id = message.chat.id
        user_email = message.text

        email_subject = "Your DollarBot Spend History"
        email_body = f"Hello {user_email},\n\nPlease find the attachment of your spend history"

        file_exist = os.path.isfile('code/data.csv')
        if file_exist:
            smtp_server = connect_to_smtp_server()
            send_email(smtp_server, user_email, email_subject, email_body, 'code/data.csv')
        else:
            file_path = extract.run(message, bot)
            smtp_server = connect_to_smtp_server()
            send_email(smtp_server, user_email, email_subject, email_body, file_path)

        close_smtp_connection(smtp_server)
        message = bot.send_message(chat_id, 'Your Email has been sent successfully!')

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise