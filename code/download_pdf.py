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

import helper
import logging
from matplotlib import pyplot as plt

# Constants
TOP_MARGIN = 0.8
LINE_HEIGHT = 0.15
FONT_SIZE_TEXT = 8

def generate_expense_history_plot(user_history):
    """
    generate_expense_history_plot(user_history): This function generates a Matplotlib plot of the user's expense history.

    Args:
        user_history (list): List of strings representing user's expense history records.

    Returns:
        fig (Matplotlib.figure.Figure): Matplotlib figure object containing the expense history plot.
    """
    try:
        fig, ax = plt.subplots()
        top = TOP_MARGIN

        if not user_history:
            ax.text(
                0.1,
                top,
                "No record found!",
                horizontalalignment="left",
                verticalalignment="center",
                transform=ax.transAxes,
                fontsize=FONT_SIZE_TEXT,
            )
        else:
            for rec in user_history:
                try:
                    date, category, amount, account = rec.split(",")
                except ValueError as ve:
                    raise ValueError(f"Error parsing user history data: {ve}")

                rec_str = f"{category} expense on {date} with {account} account is {amount}$."
                ax.text(
                    0,
                    top,
                    rec_str,
                    horizontalalignment="left",
                    verticalalignment="center",
                    transform=ax.transAxes,
                    fontsize=FONT_SIZE_TEXT,
                    bbox=dict(facecolor="blue", alpha=0.1),
                )
                top -= LINE_HEIGHT

        ax.axis("off")
        return fig

    except Exception as e:
        logging.exception(str(e))
        raise

def save_and_send_pdf(fig, chat_id, bot):
    """
    save_and_send_pdf(fig, chat_id, bot): This function saves the Matplotlib figure as a PDF and sends it as a document via Telegram.

    Args:
        fig (Matplotlib.figure.Figure): Matplotlib figure object.
        chat_id (int): Telegram chat ID.
        bot (obj): The Telegram bot object.

    Returns:
        None
    """
    try:
        pdf_path = "expense_history.pdf"
        fig.savefig(pdf_path)
        plt.close(fig)

        bot.send_message(chat_id, "expense_history.pdf is created")
        bot.send_document(chat_id, open(pdf_path, "rb"))

    except Exception as e:
        logging.exception(str(e))
        raise

def run(message, bot):
    """
    run(message, bot): This is the main function used to implement the pdf save feature.

    Args:
        message (obj): The message object received from Telegram.
        bot (obj): The Telegram bot object.

    Returns:
        None

    Raises:
        ValueError: If there is an issue parsing the user history data.
        Exception: If an unexpected error occurs during the process.

    This function generates a PDF file containing the user's expense history plot and sends it as a document using a Telegram bot.
    """
    try:
        helper.read_json()
        chat_id = message.chat.id
        user_history = helper.getUserHistory(chat_id)
        fig = generate_expense_history_plot(user_history)
        save_and_send_pdf(fig, chat_id, bot)

    except ValueError as ve:
        bot.reply_to(message, f"Oops! {ve}")

    except Exception as e:
        logging.exception(str(e))
        bot.reply_to(message, "Oops! An unexpected error occurred.")