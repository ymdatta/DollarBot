import helper
import logging
from matplotlib import pyplot as plt

def generate_expense_history_plot(user_history):
    """
    generate_expense_history_plot(user_history): This function generates a Matplotlib plot of the user's expense history.

    Args:
        user_history (list): List of strings representing user's expense history records.

    Returns:
        fig (Matplotlib.figure.Figure): Matplotlib figure object containing the expense history plot.
    """
    fig, ax = plt.subplots()
    top = 0.8

    if not user_history:
        ax.text(
            0.1,
            top,
            "No record found!",
            horizontalalignment="left",
            verticalalignment="center",
            transform=ax.transAxes,
            fontsize=20,
        )
    else:
        for rec in user_history:
            date, category, amount = rec.split(",")
            rec_str = f"{amount}$ {category} expense on {date}"
            ax.text(
                0,
                top,
                rec_str,
                horizontalalignment="left",
                verticalalignment="center",
                transform=ax.transAxes,
                fontsize=14,
                bbox=dict(facecolor="blue", alpha=0.1),
            )
            top -= 0.15

    ax.axis("off")
    return fig

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
    pdf_path = "expense_history.pdf"
    fig.savefig(pdf_path)
    plt.close(fig)

    bot.send_message(chat_id, "expense_history.pdf is created")
    bot.send_document(chat_id, open(pdf_path, "rb"))

def run(message, bot):
    """
    run(message, bot): This is the main function used to implement the pdf save feature.

    Args:
        message (obj): The message object received from Telegram.
        bot (obj): The Telegram bot object.

    Returns:
        None

    Raises:
        Exception: If an error occurs during the process.

    This function generates a PDF file containing the user's expense history plot and sends it as a document using a Telegram bot.
    """
    try:
        helper.read_json()
        chat_id = message.chat.id
        user_history = helper.getUserHistory(chat_id)
        fig = generate_expense_history_plot(user_history)
        save_and_send_pdf(fig, chat_id, bot)
    except Exception as e:
        logging.exception(str(e))
        bot.reply_to(message, str(e))