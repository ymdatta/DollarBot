import datetime
import os

import pandas as pd
import requests
from bson import ObjectId
from jose import jwt
from motor.motor_asyncio import AsyncIOMotorClient
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import MONGO_URI
from config import TELEGRAM_BOT_TOKEN
from config import TELEGRAM_BOT_API_BASE_URL

# Constants
API_BASE_URL = TELEGRAM_BOT_API_BASE_URL
TOKEN = TELEGRAM_BOT_TOKEN
BOT_USERNAME = "@moneyhandlerbot"
TSK = "None"
TOKEN_ALGORITHM = "HS256"
# MONGO_URI = os.getenv(
#     "MONGO_URI",
#     "mongodb+srv://mmdb_admin:tiaNSKxzyO2NdXts@moneymanagerdb.s2bp9.mongodb.net/"
#     "?retryWrites=true&w=majority&appName=MoneyManagerDB",
# )

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

def is_user_logged_in(user_id):
    return user_id in user_tokens

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
        await update.message.reply_text(
            "Please log in using /login command before adding expenses."
        )
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
        await update.message.reply_text(
            f"Failed to add expense. Error: {error_message}"
        )


async def view_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Placeholder function for viewing balance or account details.
    """
    await update.message.reply_text("Hello, Your balance is")


async def attempt_signup(update: Update, username: str, password: str):
    """
    Attempt to sign the user up with the provided username and password.
    """
    response = requests.post(
        f"{API_BASE_URL}/users/", json={"username": username, "password": password}
    )
    # Check if the username already exists
    existing_user = await telegram_collection.find_one({"username": username})
    if existing_user:
        await update.message.reply_text(
            "Username already exists. Please choose another one."
        )
        return

    if response.status_code == 200:
        user_id = update.message.chat_id if update.message else None
        tokenization = requests.post(
            f"{API_BASE_URL}/users/token/?token_expires=43200",
            data={"username": username, "password": password},
        )
        token = tokenization.json()["result"]["token"]

        payload = {"name": username, "balance": 0, "currency": "string"}
        account_detail = requests.post(
            f"{API_BASE_URL}/accounts/", headers={"token": token}, json=payload
        )
        account_id = account_detail.json()["account_id"]

        user_data = {
            "username": username,
            "password": password,
            "token": token,
            "telegram_id": user_id,
            "account_id": account_id,
        }
        await telegram_collection.insert_one(user_data)
        await update.message.reply_text(
            "Signup successful! You can now log in using /login."
        )
    elif response.status_code == 400:
        await update.message.reply_text(
            "Username already exists. Please choose another one."
        )
    elif response.status_code == 422:
        await update.message.reply_text(
            "Invalid credentials. Make sure to provide both a username and password."
        )
    else:
        await update.message.reply_text(f"An error occurred: {response.text}")

async def expense_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show buttons for expense actions (Add, Delete, View).
    """
    user_id = update.message.chat_id if update.message else None

    if not is_user_logged_in(user_id):
        await update.message.reply_text("Please log in using /login command to access this feature.")
        return
    
    keyboard = [
        [InlineKeyboardButton("Add Expense", callback_data="add_expense")],
        [InlineKeyboardButton("Delete Expense", callback_data="delete_expense")],
        [InlineKeyboardButton("View Expenses", callback_data="view_expenses")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Choose an action for your expenses:", reply_markup=reply_markup
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle inline button actions for expenses.
    """
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    if query.data == "add_expense":
        await add_expense_handler(query, context)
    elif query.data == "delete_expense":
        await delete_expense_handler(query, context)
    elif query.data == "view_expenses":
        await view_expenses_handler(query, context)

async def add_expense_handler(query, context):
    """
    Start the process of adding a new expense by prompting for the amount.
    """
    await query.edit_message_text("Please enter the amount:")
    context.user_data["expense_action"] = "add"
    context.user_data["expense_step"] = "amount"  # Set the next step as amount

async def process_expense_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the sequential input for adding an expense (amount, category, date).
    """
    user_id = update.message.chat_id if update.message else None
    text = update.message.text if update.message else ""
    
    if context.user_data.get("expense_action") == "add":
        # Process amount
        if context.user_data.get("expense_step") == "amount":
            try:
                # Try to parse amount as a float
                amount = float(text)
                context.user_data["amount"] = amount
                context.user_data["expense_step"] = "category"
                await update.message.reply_text("Please enter the category (e.g., Food):")
            except ValueError:
                await update.message.reply_text("Invalid amount. Please enter a numeric value.")

        # Process category
        elif context.user_data.get("expense_step") == "category":
            context.user_data["category"] = text
            context.user_data["expense_step"] = "date"
            await update.message.reply_text("Please enter the date (YYYY-MM-DD):")

        # Process date
        elif context.user_data.get("expense_step") == "date":
            try:
                # Validate date format
                date = datetime.datetime.strptime(text, "%Y-%m-%d").date()
                context.user_data["date"] = date
                # Complete the expense addition
                await finalize_expense(update, context)
            except ValueError:
                await update.message.reply_text("Invalid date format. Please enter a date in YYYY-MM-DD format.")

async def finalize_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Finalize the expense entry and clear the temporary data.
    """
    amount = context.user_data.get("amount")
    category = context.user_data.get("category")
    date = context.user_data.get("date")
    
    # Post the expense to the API or store it
    # Example for demonstration purposes
    await update.message.reply_text(
        f"Expense added successfully!\n\nAmount: {amount}\nCategory: {category}\nDate: {date}"
    )
    
    # Clear user data for expense entry
    context.user_data.pop("expense_action", None)
    context.user_data.pop("expense_step", None)
    context.user_data.pop("amount", None)
    context.user_data.pop("category", None)
    context.user_data.pop("date", None)

async def delete_expense_handler(query, context):
    """
    Handle deleting an expense.
    """
    await query.edit_message_text("Please enter the ID or description of the expense to delete:")
    context.user_data["expense_action"] = "delete"

async def view_expenses_handler(query, context):
    """
    Handle viewing expenses.
    """
    # Retrieve and display the expense list (this example shows a placeholder message)
    # You can fetch actual expenses from your database and format them here.
    expense_list = "1. Food - $50\n2. Transport - $15"
    await query.edit_message_text(f"Here are your recent expenses:\n\n{expense_list}")

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
    response = requests.post(
        f"{API_BASE_URL}/users/token/?token_expires=43200",
        data={"username": username, "password": password},
    )
    if response.status_code == 200:
        # token = response.json().get("access_token")
        user_id = update.message.chat_id if update.message else None

        user = await telegram_collection.find_one(
            {"username": username, "password": password}
        )
        user_tokens[user_id] = user["token"]
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
        await update.message.reply_text(
            "Please log in using /login command to view categories."
        )
        return

    token = user_tokens[user_id]
    headers = {"token": token}

    # Fetch categories from API
    response = requests.get(f"{API_BASE_URL}/categories/", headers=headers)
    if response.status_code == 200:
        categories_data = response.json().get("categories", {})

        # Prepare table header and rows with fixed-width formatting
        header = f"{'Category':<20} {'Monthly Budget':>15}\n"
        separator = "-" * 35
        rows = [
            f"{category:<20} {details['monthly_budget']:>15.2f}"
            for category, details in categories_data.items()
        ]

        # Combine header, separator, and rows into one string
        table_str = (
            f"Here are your available categories with budgets:\n\n```\n{header}{separator}\n"
            + "\n".join(rows)
            + "\n```"
        )

        # Send the formatted table as a message with monospaced font
        await update.message.reply_text(table_str, parse_mode="MarkdownV2")
    else:
        error_message = response.json().get("detail", "Unable to fetch categories.")
        await update.message.reply_text(f"Error: {error_message}")

async def fallback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Unrecognized command")


async def combined_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle incoming text messages for either general handling or processing expense input,
    based on the user's context.
    """
    user_id = update.message.chat_id if update.message else None
    text = update.message.text if update.message else ""

    # Check if the user is in the middle of adding an expense
    if context.user_data.get("expense_action") == "add":
        # Process expense input
        if context.user_data.get("expense_step") == "amount":
            try:
                # Try to parse amount as a float
                amount = float(text)
                context.user_data["amount"] = amount
                context.user_data["expense_step"] = "category"
                await update.message.reply_text("Please enter the category (e.g., Food):")
            except ValueError:
                await update.message.reply_text("Invalid amount. Please enter a numeric value.")

        elif context.user_data.get("expense_step") == "category":
            context.user_data["category"] = text
            context.user_data["expense_step"] = "date"
            await update.message.reply_text("Please enter the date (YYYY-MM-DD):")

        elif context.user_data.get("expense_step") == "date":
            try:
                # Validate date format
                date = datetime.datetime.strptime(text, "%Y-%m-%d").date()
                context.user_data["date"] = date
                await finalize_expense(update, context)
            except ValueError:
                await update.message.reply_text("Invalid date format. Please enter a date in YYYY-MM-DD format.")
    
    else:
        # If not in expense input process, handle as a general message
        await handle_message(update, context)


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
    app.add_handler(CommandHandler("expense", expense_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, combined_handler))
    # app.add_handler(MessageHandler(filters.TEXT, handle_message))
    # app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, process_expense_input))
    app.add_handler(MessageHandler(filters.COMMAND, fallback_command))
    app.add_error_handler(error)
    print("Polling..")
    app.run_polling(poll_interval=3)
