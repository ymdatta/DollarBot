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

# Global dictionaries to track login and signup states and temporarily store usernames and passwords
LOGIN_STATE = {}
SIGNUP_STATE = {}
USERNAMES = {}
PASSWORDS = {}

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
    Initiate the login process, prompting for the username first.
    """
    user_id = update.message.chat_id if update.message else None
    LOGIN_STATE[user_id] = "awaiting_username"
    await update.message.reply_text("Please enter your username:")

async def signup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Initiate the signup process, prompting for the username first.
    """
    user_id = update.message.chat_id if update.message else None
    SIGNUP_STATE[user_id] = "awaiting_username"
    await update.message.reply_text("To sign up, please enter your desired username:")


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

async def attempt_signup(update: Update, username: str, password: str):
    """
    Attempt to sign the user up with the provided username and password.
    """
    response = requests.post(f"{API_BASE_URL}/users/", json={"username": username, "password": password})
    # Check if the username already exists
    existing_user = await telegram_collection.find_one({"username": username})
    if existing_user:
        await update.message.reply_text("Username already exists. Please choose another one.")
        return


    if response.status_code == 200:
        user_id = update.message.chat_id if update.message else None
        tokenization = requests.post(
            f"{API_BASE_URL}/users/token/?token_expires=43200",
            data={"username": username, "password": password}
        )
        token = tokenization.json()["result"]["token"]

        payload = {
            "name": username,
            "balance": 0,
            "currency": "string"
        }
        account_detail = requests.post(f"{API_BASE_URL}/accounts/", headers={"token": token}, json=payload)
        account_id = account_detail.json()['account_id']

        user_data = {
            "username": username,
            "password": password,
            "token": token,
            "telegram_id": user_id,
            "account_id":account_id,
        }
        await telegram_collection.insert_one(user_data)
        await update.message.reply_text("Signup successful! You can now log in using /login.")
    elif response.status_code == 400:
        await update.message.reply_text("Username already exists. Please choose another one.")
    elif response.status_code == 422:
        await update.message.reply_text("Invalid credentials. Make sure to provide both a username and password.")
    else:
        await update.message.reply_text(f"An error occurred: {response.text}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle incoming text messages and direct messages to appropriate handlers based on context.
    """
    user_id = update.message.chat_id if update.message else None
    text = update.message.text if update.message else ""

    # Check if user is in the signup process
    if user_id in SIGNUP_STATE:
        if SIGNUP_STATE[user_id] == "awaiting_username":
            # Store the username and prompt for password
            USERNAMES[user_id] = text
            SIGNUP_STATE[user_id] = "awaiting_password"
            await update.message.reply_text("Please enter your desired password:")

        elif SIGNUP_STATE[user_id] == "awaiting_password":
            # Retrieve username and password, then attempt signup
            username = USERNAMES.get(user_id)
            password = text
            await attempt_signup(update, username, password)
            # Clear signup state after attempting signup
            SIGNUP_STATE.pop(user_id, None)
            USERNAMES.pop(user_id, None)
        return

    # Check if user is in login process
    if user_id in LOGIN_STATE:
        if LOGIN_STATE[user_id] == "awaiting_username":
            # Store the username and prompt for password
            USERNAMES[user_id] = text
            LOGIN_STATE[user_id] = "awaiting_password"
            await update.message.reply_text("Please enter your password:")

        elif LOGIN_STATE[user_id] == "awaiting_password":
            # Retrieve username and password, then attempt login
            username = USERNAMES.get(user_id)
            password = text
            await attempt_login(update, username, password)
            # Clear login state after attempting login
            LOGIN_STATE.pop(user_id, None)
            USERNAMES.pop(user_id, None)
        return

        await handle_response(update, text)

async def attempt_login(update: Update, username: str, password: str):
    """
    Attempt to log the user in with the provided username and password.
    """
    response = requests.post(f"{API_BASE_URL}/users/token/?token_expires=43200", data={"username": username, "password": password})
    if response.status_code == 200:
        # token = response.json().get("access_token")
        user_id = update.message.chat_id if update.message else None

        user = await telegram_collection.find_one({"username": username, "password": password})
        user_tokens[user_id]= user["token"]
        user_tokens["account"] = user["account_id"]
        print(user_tokens)

        await update.message.reply_text("Login successful!")
    else:
        await update.message.reply_text("Login failed. Please check your credentials.")


async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /categories command, providing a list of categories.
    """
    user_id = update.message.chat_id

    if user_id not in user_tokens:
        await update.message.reply_text("Please log in using /login command to view categories.")
        return

    token = user_tokens[user_id]
    headers = {"token":token}

    category = requests.get(f"{API_BASE_URL}/categories/", headers=headers)
    if category.status_code == 200:
        categories = category.json()["categories"]
        await update.message.reply_text(f"Available Categories:")
        print(categories.keys())
        for i in categories.keys():
            await update.message.reply_text(f"•{i}")
    else:
        error_message = category.json().get("detail", "Unable to fetch categories.")
        await update.message.reply_text(f"Error: {error_message}")


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
    app.add_handler(CommandHandler("see_categories", categories_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)
    print("Polling..")
    app.run_polling(poll_interval=3)
