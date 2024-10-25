from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "7217139754:AAGTo4BtF2obYrxm_MsHmXLekxvnNQ8F3fs"
BOT_USERNAME = "@moneyhandlerbot"

#commands

async def start_command(update:Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, Welcome to the MoneyHandler")

async def add_command(update:Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, Please add the money")

async def view_command(update:Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, YOur balance is")

#handle resopnses

def handle_response(text: str):
    return "We are working on it"

async def handle_message(update:Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text

    print(f' User {update.message.chat.id} in {message_type}: "{text}"')

    if message_type == "group":
        if BOT_USERNAME in text:
            new_text = text.replace(BOT_USERNAME, '').strip()
            response = handle_response(new_text)
        else:
            return
    else:
        response = handle_response(text)
    
    print('Bot:', response)
    await update.message.reply_text(response)

async def error(update:Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Updat {update} caused error {context.error}')

if __name__ == '__main__':
    print("Starting Bot..")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('add', add_command))
    app.add_handler(CommandHandler('view', view_command))

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.add_error_handler(error)
    print('Polling..')
    app.run_polling(poll_interval=3)



# def start(update: Update, context):
#     update.message.reply_text('Welcome to MoneyManager bot!')

# def main():
#     TOKEN = "7217139754:AAGTo4BtF2obYrxm_MsHmXLekxvnNQ8F3fs"
#     bot = Bot(TOKEN)
#     update_queue = Queue()
#     dispatcher = Dispatcher(bot, update_queue, use_context=True)
#     dispatcher.add_handler(CommandHandler("start", start))
#     # dispatcher.add_handler(CommandHandler("balance", get_balance))
#     bot.start_polling()

# if __name__ == '__main__':
#     main()
