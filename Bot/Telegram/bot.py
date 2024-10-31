import os
import datetime
import requests
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from jose import jwt

# Constants
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

# MongoDB setup
client = AsyncIOMotorClient(MONGO_URI)
db = client.mmdb
users_collection = db.users
tokens_collection = db.tokens
accounts_collection = db.accounts
expenses_collection = db.expenses
telegram_collection = db.Telegram
user_tokens = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /start command, providing a welcome message and instructions to log in.
    """
    if update.message:
        await update.message.reply_text(
            "Welcome to MoneyHandler! Please log in using /login <username> <password>"
        )


async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Set the task to "Login" and prompt the user to provide login credentials.
    """
    global TSK
    TSK = "Login"
    if update.message:
        await update.message.reply_text(
            "Please enter your username and password in the format: <username> <password>"
        )


async def signup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Set the task to "Signup" and prompt the user to provide signup credentials.
    """
    global TSK
    TSK = "Signup"
    if update.message:
        await update.message.reply_text("Please sign up using /login command before adding expenses.")


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Check if the user is authenticated, then handle adding an expense.
    If the user is not logged in, prompt them to log in first.
    """
    user_id = update.message.chat_id if update.message else None
    if user_id not in user_tokens:
        await update.message.reply_text("Please log in using /login command before adding expenses.")
        return

    # Token for the authenticated user
    token = user_tokens[user_id]
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_BASE_URL}/expenses/",
        json={"amount": 100, "currency": "USD", "category": "Food"},
        headers=headers,
    )

    if response.status_code == 200:
        await update.message.reply_text("Expense added successfully!")
    else:
        error_message = response.json().get("detail", "Unknown error")
        await update.message.reply_text(f"Failed to add expense. Error: {error_message}")


async def view_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Placeholder function for viewing balance or account details.
    """
    await update.message.reply_text("Hello, Your balance is")


async def handle_response(update: Update, text: str):
    """
    Handle user input based on the current task (e.g., Signup, Login).
    """
    global TSK
    if TSK == "Signup":
        await handle_signup(update, text)
    elif TSK == "Login":
        await handle_login(update, text)
    else:
        await update.message.reply_text("Sorry, I didn't understand that command. Please use /help to see available commands.")


async def handle_signup(update: Update, text: str):
    """
    Handle user signup by creating an account and storing the user data in MongoDB.
    """
    user_input = text.split()
    username, password = user_input[0], user_input[1]
    response = requests.post(f"{API_BASE_URL}/users/", json={"username": username, "password": password})

    if response.status_code == 200:
        user_id = update.message.chat_id if update.message else None
        tokenization = requests.post(
            f"{API_BASE_URL}/users/token/?token_expires=43200",
            data={"username": username, "password": password}
        )
        token = tokenization.json()["result"]["token"]

        user_data = {
            "username": username,
            "password": password,
            "token": token,
            "telegram_id": user_id,
        }
        await telegram_collection.insert_one(user_data)
        await update.message.reply_text("User created successfully! You can now log in using /login.")
    elif response.status_code == 400:
        await update.message.reply_text("Username already exists. Please choose another one.")
    elif response.status_code == 422:
        await update.message.reply_text("Invalid credentials. Make sure to provide both a username and password.")
    else:
        await update.message.reply_text(f"An error occurred: {response.text}")


async def handle_login(update: Update, text: str):
    """
    Handle user login by authenticating the user and retrieving their access token.
    """
    user_input = text.split()
    username, password = user_input[0], user_input[1]
    response = requests.post(f"{API_BASE_URL}/token/", data={"username": username, "password": password})

    if response.status_code == 200:
        token = response.json().get("access_token")
        user_id = update.message.chat_id if update.message else None
        user_tokens[user_id] = token
        await update.message.reply_text("Login successful!")
    else:
        await update.message.reply_text("Login failed. Please check your credentials.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle incoming text messages and direct messages to appropriate handlers based on context.
    """
    message_type = update.message.chat.type if update.message else None
    text = update.message.text if update.message else ""

    if message_type == "group" and BOT_USERNAME in text:
        new_text = text.replace(BOT_USERNAME, '').strip()
        await handle_response(update, new_text)
    elif message_type == "private":
        await handle_response(update, text)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Log and handle errors that occur during the bot's operation.
    """
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
