import helper
import logging
from matplotlib import pyplot as plt

def generate_expense_history_plot(user_history):
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
   
    pdf_path = "expense_history.pdf"
    fig.savefig(pdf_path)
    plt.close(fig)

    bot.send_message(chat_id, "expense_history.pdf is created")
    bot.send_document(chat_id, open(pdf_path, "rb"))

def run(message, bot):
    
    try:
        helper.read_json()
        chat_id = message.chat.id
        user_history = helper.getUserHistory(chat_id)
        fig = generate_expense_history_plot(user_history)
        save_and_send_pdf(fig, chat_id, bot)
    except Exception as e:
        logging.exception(str(e))
        bot.reply_to(message, str(e))