import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import requests
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import datetime
from jose import jwt

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

# MongoDB collections for user and token management
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
    """
    Handle the /start command, providing a welcome message and instructions to log in.
    """
    await update.message.reply_text("Welcome to MoneyHandler! Please log in using /login <username> <password>")


async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Set the task to "Login" and prompt the user to provide login credentials.
    """
    print("Login command called.")
    global TSK
    TSK = "Login"
    await update.message.reply_text("Please enter your username and password in the format: <username> <password>")


async def signup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Set the task to "Signup" and prompt the user to provide signup credentials.
    """
    print("Signup command called.")
    global TSK
    TSK = "Signup"
    await update.message.reply_text("Please sign up using /login command before adding expenses.")


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Check if the user is authenticated, then handle adding an expense.
    If the user is not logged in, prompt them to log in first.
    """
    user_id = update.message.chat_id

    # Check if user is authenticated
    if user_id not in user_tokens:
        await update.message.reply_text("Please log in using /login command before adding expenses.")
        return

    # Token for the authenticated user
    token = user_tokens[user_id]

    # Adding an expense with a default payload (modify as needed)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_BASE_URL}/expenses/",
        json={"amount": 100, "currency": "USD", "category": "Food"},
        headers=headers
    )

    if response.status_code == 200:
        await update.message.reply_text("Expense added successfully!")
    else:
        await update.message.reply_text(f"Failed to add expense. Error: {response.json().get('detail', 'Unknown error')}")


async def view_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Placeholder function for viewing balance or account details.
    """
    await update.message.reply_text("Hello, Your balance is")


async def handle_response(update: Update, text: str):
    """
    Handle user input based on the current task (e.g., Signup, Login).
    If task is "Signup", attempt to register the user.
    If task is "Login", authenticate the user and retrieve their access token.
    """
    global TSK
    print(TSK)
    
    # Handle Signup task
    if TSK == "Signup":
        user_input = text.split()
        username, password = user_input[0], user_input[1]
        print(f"Username: {username}, Password: {password}")
        response = requests.post(f"{API_BASE_URL}/users/", json={"username": username, "password": password})

        if response.status_code == 200:
            print(1)
            user_id = update.message.chat_id
            tokenization = requests.post(
                f"{API_BASE_URL}/users/token/?token_expires=43200",
                data={"username": username, "password": password}
            )
            token = tokenization.json()['result']['token']
            print(token)

            user_data = {
                "username": username,
                "password": password,
                "token": token,
                "telegram_id": update.message.chat.id,
            }

            await telegram_collection.insert_one(user_data)
            await update.message.reply_text("User created successfully! You can now log in using /login.")

        elif response.status_code == 400:
            print(2)
            await update.message.reply_text("Username already exists. Please choose another one.")
        elif response.status_code == 422:
            print(3)
            await update.message.reply_text("Invalid credentials. Make sure to provide both a username and password.")
        else:
            await update.message.reply_text(f"An error occurred: {response.text}")

    # Handle Login task
    elif TSK == "Login":
        user_input = text.split()
        username, password = user_input[0], user_input[1]
        print(f"Logging in with Username: {username}, Password: {password}")
        response = requests.post(f"{API_BASE_URL}/token/", data={"username": username, "password": password})

        if response.status_code == 200:
            token = response.json().get("access_token")
            user_id = update.message.chat_id
            user_tokens[user_id] = token  # Store token for the user
            await update.message.reply_text("Login successful!")
    else:
        await update.message.reply_text("Sorry, I didn't understand that command. Please use /help to see available commands.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle incoming text messages, checking for group mentions of the bot or processing single messages.
    Directs messages to the appropriate handler based on context.
    """
    message_type = update.message.chat.type
    text = update.message.text

    print(f' User {update.message.chat.id} in {message_type}: "{text}"')

    if message_type == "group":
        if BOT_USERNAME in text:
            new_text = text.replace(BOT_USERNAME, '').strip()
            await handle_response(new_text)  # Pass the 'new_text' as argument
        else:
            return
    else:
        global TSK
        print(TSK)
        await handle_response(update, text)  # Pass the 'text' as argument here

    print("Bot response sent")


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
    app.add_handler(CommandHandler('signup', signup_command))

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.add_error_handler(error)
    print("Polling..")
    app.run_polling(poll_interval=3)
