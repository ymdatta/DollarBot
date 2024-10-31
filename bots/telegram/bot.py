import datetime
import os

import requests
from bson import ObjectId
from jose import jwt
from motor.motor_asyncio import AsyncIOMotorClient
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

API_BASE_URL = "http://localhost:8000"
TOKEN = "7217139754:AAGTo4BtF2obYrxm_MsHmXLekxvnNQ8F3fs"
BOT_USERNAME = "@moneyhandlerbot"
TSK = "None"
TOKEN_ALGORITHM = "HS256"
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://mmdb_admin:tiaNSKxzyO2NdXts@moneymanagerdb.s2bp9.mongodb.net/"
    "?retryWrites=true&w=majority&appName=MoneyManagerDB",
)


user_tokens = {}

# MongoDB setup
client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URI)
db = client.mmdb
users_collection = db.users
tokens_collection = db.tokens
accounts_collection = db.accounts
expenses_collection = db.expenses
telegram_collection = db.Telegram


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to MoneyHandler! Please log in using /login <username> <password>"
    )


async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Login command called.")
    global TSK
    TSK = "Login"
    await update.message.reply_text(
        "Please enter your username and password in the format: <username> <password>"
    )


async def signup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Signup command called.")
    global TSK
    TSK = "Signup"
    await update.message.reply_text(
        "Please sign up using /login command before adding expenses."
    )


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    # Check if user is authenticated
    if user_id not in user_tokens:
        await update.message.reply_text(
            "Please log in using /login command before adding expenses."
        )
        return

    # Token for the authenticated user
    token = user_tokens[user_id]

    # Example of adding an expense
    # Modify according to your needs
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_BASE_URL}/expenses/",
        json={"amount": 100, "currency": "USD", "category": "Food"},
        headers=headers,
    )

    if response.status_code == 200:
        await update.message.reply_text("Expense added successfully!")
    else:
        await update.message.reply_text(
            f"Failed to add expense. Error: {response.json().get('detail', 'Unknown error')}"
        )


async def view_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, YOur balance is")


# handle resopnses


async def handle_response(update: Update, text: str):
    global TSK
    print(TSK)
    if TSK == "Signup":
        user_input = text.split()
        username, password = user_input[0], user_input[1]
        print(f"Username: {username}, Password: {password}")
        response = requests.post(
            f"{API_BASE_URL}/users/", json={"username": username, "password": password}
        )

        if response.status_code == 200:
            print(1)
            user_id = update.message.chat_id
            tokenization = requests.post(
                f"{API_BASE_URL}/users/token/?token_expires=43200",
                data={"username": "hellothere", "password": "hello htere"},
            )
            token = tokenization.json()["result"]["token"]
            print(token)

            user_data = {
                "username": username,
                "password": password,
                "token": token,
                "telegram_id": update.message.chat.id,
            }

            await telegram_collection.insert_one(user_data)
            await update.message.reply_text(
                "User created successfully! You can now log in using /login."
            )

        elif response.status_code == 400:
            print(2)
            await update.message.reply_text(
                "Username already exists. Please choose another one."
            )
        elif response.status_code == 422:
            print(3)
            await update.message.reply_text(
                "Invalid credentials. Make sure to provide both a username and password."
            )
        else:
            await update.message.reply_text(f"An error occurred: {response.text}")

    elif TSK == "Login":
        user_input = text.split()
        username, password = user_input[0], user_input[1]
        print(f"Logging in with Username: {username}, Password: {password}")
        response = requests.post(
            f"{API_BASE_URL}/token/", data={"username": username, "password": password}
        )

        if response.status_code == 200:
            token = response.json().get("access_token")
            user_id = update.message.chat_id
            user_tokens[user_id] = token  # Store token for the user
            await update.message.reply_text("Login successful!")
    else:
        await update.message.reply_text(
            "Sorry, I didn't understand that command. Please use /help to see available commands."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text

    print(f' User {update.message.chat.id} in {message_type}: "{text}"')

    if message_type == "group":
        if BOT_USERNAME in text:
            new_text = text.replace(BOT_USERNAME, "").strip()
            await handle_response(new_text)  # Pass the 'new_text' as argument
        else:
            return
    else:
        global TSK
        print(TSK)
        await handle_response(update, text)  # Pass the 'text' as argument here

    print("Bot response sent")

    # print('Bot:', response)
    # await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")


if __name__ == "__main__":
    print("Starting Bot..")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("add", add_command))
    app.add_handler(CommandHandler("login", login_command))
    app.add_handler(CommandHandler("signup", signup_command))

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.add_error_handler(error)
    print("Polling..")
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
