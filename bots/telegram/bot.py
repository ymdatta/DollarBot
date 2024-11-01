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
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import MONGO_URI, TELEGRAM_BOT_API_BASE_URL, TELEGRAM_BOT_TOKEN

# Constants
API_BASE_URL = TELEGRAM_BOT_API_BASE_URL
TOKEN = TELEGRAM_BOT_TOKEN
BOT_USERNAME = "@moneyhandlerbot"
TSK = "None"
TOKEN_ALGORITHM = "HS256"

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


# Authentication check decorator
def requires_auth(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        print("Checking auth")
        user_id = update.message.chat_id
        print(user_id)
        user = await telegram_collection.find_one({"telegram_id": user_id})
        print(user)
        if user and user.get("token"):
            return await func(update, context, *args, **kwargs, token=user.get("token"))
        else:
            await update.message.reply_text("You are not authenticated. Please /login")
    return wrapper


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /start command, providing a welcome message and instructions to log in.
    """
    if update.message:
        await update.message.reply_text(
            "Welcome to Money Manager! Please singup using /signup or log in using /login"
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

    if response.status_code == 200:
        print("SIGNUP", username, password)
        user_id = update.message.chat_id if update.message else None
        tokenization = requests.post(
            f"{API_BASE_URL}/users/token/?token_expires=43200",
            data={"username": username, "password": password},
        )
        token = tokenization.json()["result"]["token"]

        user_data = {
            "username": username,
            "token": token,
            "telegram_id": user_id,
        }

        existing_user = await telegram_collection.find_one({"telegram_id": user_id})
        if existing_user:
            await telegram_collection.update_one(
                {"telegram_id": user_id}, {"$set": user_data}
            )
        else:
            await telegram_collection.insert_one(user_data)

        await update.message.reply_text(
            "Signup successful! You can now log in using /login."
        )
        return 
    await update.message.reply_text(f"An error occurred: {response.json().get('detail', 'Unknown error')}")


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
        await update.message.reply_text(
            "Please log in using /login command to access this feature."
        )
        return

    keyboard = [
        [InlineKeyboardButton("Add Expense", callback_data="add_expense")],
        [InlineKeyboardButton("Delete Expense", callback_data="delete_expense")],
        [InlineKeyboardButton("View Expenses", callback_data="view_expenses")],
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
                await update.message.reply_text(
                    "Please enter the category (e.g., Food):"
                )
            except ValueError:
                await update.message.reply_text(
                    "Invalid amount. Please enter a numeric value."
                )

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
                await update.message.reply_text(
                    "Invalid date format. Please enter a date in YYYY-MM-DD format."
                )


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
    await query.edit_message_text(
        "Please enter the ID or description of the expense to delete:"
    )
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
    Show buttons for category actions (View, Add, Edit, Delete).
    """
    
    keyboard = [
        [InlineKeyboardButton("View Categories", callback_data="view_category")],
        [InlineKeyboardButton("Add Category", callback_data="add_category")],
        [InlineKeyboardButton("Edit Category", callback_data="edit_category")],
        [InlineKeyboardButton("Delete Category", callback_data="delete_category")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Choose an action for categories:", reply_markup=reply_markup
    )


async def category_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle inline button actions for categories.
    """
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    if query.data == "view_category":
        await view_category_handler(query, context)
    elif query.data == "add_category":
        await add_category_handler(query, context)
    elif query.data == "edit_category":
        await edit_category_handler(query, context)
    elif query.data == "delete_category":
        await delete_category_handler(query, context)


async def view_category_handler(query, context):
    """
    Handle viewing categories with table format.
    """
    user_id = query.message.chat_id
    if user_id not in user_tokens:
        await query.edit_message_text("Please log in to view categories.")
        return

    token = user_tokens[user_id]
    headers = {"token": token}
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
        await query.edit_message_text(table_str, parse_mode="MarkdownV2")
    else:
        error_message = response.json().get("detail", "Unable to fetch categories.")
        await query.edit_message_text(f"Error: {error_message}")


async def add_category_handler(query, context):
    """
    Handle adding a new category.
    """
    user_id = query.message.chat_id
    if user_id not in user_tokens:
        await query.edit_message_text("Please log in to view categories.")
        return
    

    await query.edit_message_text("Please enter the name of the new category:")
    context.user_data["category_action"] = "add"
    context.user_data["category_step"] = "add_name"


async def edit_category_handler(query, context):
    """
    Display the user's categories as inline buttons to select for editing.
    """
    user_id = query.message.chat_id
    if user_id not in user_tokens:
        await query.edit_message_text("Please log in to edit categories.")
        return

    token = user_tokens[user_id]
    headers = {"token": token}
    response = requests.get(f"{API_BASE_URL}/categories/", headers=headers)

    if response.status_code == 200:
        categories_data = response.json().get("categories", {})

        # Create buttons for each category
        keyboard = [
            [InlineKeyboardButton(category, callback_data=f"edit_{category}")]
            for category in categories_data.keys()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Select a category to edit:", reply_markup=reply_markup
        )
        context.user_data["category_action"] = "edit"
    else:
        error_message = response.json().get("detail", "Unable to fetch categories.")
        await query.edit_message_text(f"Error: {error_message}")

async def handle_edit_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the selection of a category for editing and prompt for a new budget.
    """
    query = update.callback_query
    await query.answer()  # Acknowledge the callback
    selected_category = query.data.replace("edit_", "")
    
    # Store the selected category and set up for the next step to enter a new budget
    context.user_data["selected_category"] = selected_category
    context.user_data["category_action"] = "edit"
    context.user_data["category_step"] = "edit_budget"  # Set the next expected step

    # Prompt the user to enter the new budget
    await query.edit_message_text(
        f"Enter the new monthly budget for {selected_category}:"
    )


async def delete_category_handler(query, context):
    """
    Display the user's categories as inline buttons for deletion.
    """
    user_id = query.message.chat_id
    if user_id not in user_tokens:
        await query.edit_message_text("Please log in to delete categories.")
        return

    token = user_tokens[user_id]
    headers = {"token": token}
    response = requests.get(f"{API_BASE_URL}/categories/", headers=headers)

    if response.status_code == 200:
        categories_data = response.json().get("categories", {})

        # Create buttons for each category
        keyboard = [
            [InlineKeyboardButton(category, callback_data=f"delete_{category}")]
            for category in categories_data.keys()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Select a category to delete:", reply_markup=reply_markup
        )
        context.user_data["category_action"] = "delete"
    else:
        error_message = response.json().get("detail", "Unable to fetch categories.")
        await query.edit_message_text(f"Error: {error_message}")

async def handle_delete_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the selection of a category for deletion and confirm deletion.
    """
    query = update.callback_query
    await query.answer()  # Acknowledge the callback
    selected_category = query.data.replace("delete_", "")

    # Confirm deletion with the user
    user_id = query.message.chat_id
    token = user_tokens[user_id]
    headers = {"token": token}
    response = requests.delete(f"{API_BASE_URL}/categories/{selected_category}", headers=headers)

    if response.status_code == 200:
        await query.edit_message_text(f"The category '{selected_category}' has been successfully deleted.")
    else:
        error_message = response.json().get("detail", "Failed to delete category.")
        await query.edit_message_text(f"Error: {error_message}")

async def delete_selected_category(query, context, selected_category):
    """
    Delete the specified category and notify the user of the result.
    """
    user_id = query.message.chat_id
    token = user_tokens.get(user_id)
    
    # Ensure the user is authenticated
    if not token:
        await query.edit_message_text("Please log in to delete categories.")
        return

    # Set up headers for the request
    headers = {"token": token}
    response = requests.delete(f"{API_BASE_URL}/categories/{selected_category}", headers=headers)

    # Handle the response
    if response.status_code == 200:
        await query.edit_message_text(f"The category '{selected_category}' has been successfully deleted.")
    else:
        error_message = response.json().get("detail", "Failed to delete category.")
        await query.edit_message_text(f"Error: {error_message}")


async def fallback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Unrecognized command")


async def view_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sample function to view categories.
    """
    # Sample categories data for demonstration
    categories_data = {
        "Food": {"monthly_budget": 200},
        "Transport": {"monthly_budget": 100},
        "Entertainment": {"monthly_budget": 150},
    }

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

async def finalize_category_addition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Finalize adding a new category by making an API request and confirm to the user.
    """
    user_id = update.message.chat_id if update.message else None
    token = user_tokens[user_id]

    if not token:
        await update.message.reply_text("Please log in to add a category.")
        return

    new_category_name = context.user_data.get("new_category_name")
    new_category_budget = context.user_data.get("new_category_budget")

    # Prepare headers and payload for the API request
    headers = {
        "accept": "application/json",
        "token": token,
        "Content-Type": "application/json"
    }
    payload = {
        "name": new_category_name,
        "monthly_budget": new_category_budget
    }

    # Log request details for debugging
    print("Sending request to add category")
    print(f"Headers: {headers}")
    print(f"Payload: {payload}")
    print(f"API Endpoint: https://frightening-orb-747j6q4gjjqcwr7j-9999.app.github.dev/categories/")

    try:
        # Send the request to add the category
        response = requests.post(
            f"{API_BASE_URL}/categories/",
            json=payload,
            headers=headers
        )
        
        # Log response details
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")

        if response.status_code == 200:
            await update.message.reply_text(
                f"New category added successfully!\n\nCategory: {new_category_name}\nMonthly Budget: {new_category_budget}"
            )
        else:
            error_message = response.json().get("detail", "An error occurred while adding the category.")
            await update.message.reply_text(f"Failed to add category. Error: {error_message}")

    except Exception as e:
        print(f"An error occurred: {e}")
        await update.message.reply_text("An unexpected error occurred while trying to add the category.")

    # Clear category addition state
    context.user_data.pop("category_action", None)
    context.user_data.pop("category_step", None)
    context.user_data.pop("new_category_name", None)
    context.user_data.pop("new_category_budget", None)

async def combined_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Combined handler for handling category and expense inputs step-by-step.
    """
    user_id = update.message.chat_id if update.message else None
    text = update.message.text if update.message else ""

    # Check if the user is in the process of adding an expense
    if context.user_data.get("expense_action") == "add":
        # Process expense input step by step
        if context.user_data.get("expense_step") == "amount":
            try:
                amount = float(text)
                context.user_data["amount"] = amount
                context.user_data["expense_step"] = "category"
                await update.message.reply_text("Please enter the category (e.g., Food):")
            except ValueError:
                await update.message.reply_text("Invalid amount. Please enter a numeric value.")
            return

        elif context.user_data.get("expense_step") == "category":
            context.user_data["category"] = text
            context.user_data["expense_step"] = "date"
            await update.message.reply_text("Please enter the date (YYYY-MM-DD):")
            return

        elif context.user_data.get("expense_step") == "date":
            try:
                date = datetime.datetime.strptime(text, "%Y-%m-%d").date()
                context.user_data["date"] = date
                await finalize_expense(update, context)
            except ValueError:
                await update.message.reply_text("Invalid date format. Please enter a date in YYYY-MM-DD format.")
            return

    # Check if the user is in the process of adding a new category
    elif context.user_data.get("category_action") == "add":
        # Category addition flow: Step-by-step inputs
        if context.user_data.get("category_step") == "add_name":
            context.user_data["new_category_name"] = text
            context.user_data["category_step"] = "add_budget"
            await update.message.reply_text("Please enter the monthly budget for this category:")
            return

        elif context.user_data.get("category_step") == "add_budget":
            try:
                monthly_budget = float(text)
                context.user_data["new_category_budget"] = monthly_budget
                await finalize_category_addition(update, context)
            except ValueError:
                await update.message.reply_text("Invalid budget. Please enter a numeric value.")
            return

    # Check if the user is in the process of editing a category's budget
    elif context.user_data.get("category_action") == "edit":
        # Editing category flow: Prompt for a new budget after category selection
        if context.user_data.get("category_step") == "edit_budget":
            try:
                new_budget = float(text)
                selected_category = context.user_data.get("selected_category")
                
                # Update the category budget in the database
                token = user_tokens[user_id]
                headers = {"token": token}
                payload = {"name": selected_category, "monthly_budget": new_budget}
                response = requests.put(f"{API_BASE_URL}/categories/{selected_category}", headers=headers, json=payload)

                if response.status_code == 200:
                    await update.message.reply_text(
                        f"The budget for {selected_category} has been updated to {new_budget}."
                    )
                else:
                    error_message = response.json().get("detail", "Failed to update category.")
                    await update.message.reply_text(f"Error: {error_message}")
                
            except ValueError:
                await update.message.reply_text("Invalid budget. Please enter a numeric value.")
            
            # Clear context data after updating
            context.user_data.pop("category_action", None)
            context.user_data.pop("category_step", None)
            context.user_data.pop("selected_category", None)
            return

    # Check if the user is in the signup process
    elif user_id in SIGNUP_STATE:
        if SIGNUP_STATE[user_id] == "awaiting_username":
            USERNAMES[user_id] = text
            SIGNUP_STATE[user_id] = "awaiting_password"
            await update.message.reply_text("Please enter your desired password:")
        elif SIGNUP_STATE[user_id] == "awaiting_password":
            username = USERNAMES.get(user_id)
            password = text
            await attempt_signup(update, username, password)
            SIGNUP_STATE.pop(user_id, None)
            USERNAMES.pop(user_id, None)
        return

    # Check if the user is in the login process
    elif user_id in LOGIN_STATE:
        if LOGIN_STATE[user_id] == "awaiting_username":
            USERNAMES[user_id] = text
            LOGIN_STATE[user_id] = "awaiting_password"
            await update.message.reply_text("Please enter your password:")
        elif LOGIN_STATE[user_id] == "awaiting_password":
            username = USERNAMES.get(user_id)
            password = text
            await attempt_login(update, username, password)
            LOGIN_STATE.pop(user_id, None)
            USERNAMES.pop(user_id, None)
        return

    # Handle general messages or unrecognized commands
    else:
        await handle_general_message(update, context)

async def unified_callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Unified handler for all callback queries related to categories and expenses.
    """
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    # Debugging print to check if the handler is triggered
    print("CallbackQueryHandler triggered with data:", query.data)

    data = query.data  # The callback data from the button clicked

    # Handle the different callback actions
    if data == "edit_category":
        await edit_category_handler(query, context)
    elif data == "delete_category":
        await delete_category_handler(query, context)
    elif data.startswith("edit_"):
        selected_category = data.replace("edit_", "")
        context.user_data["selected_category"] = selected_category
        context.user_data["category_action"] = "edit"
        context.user_data["category_step"] = "edit_budget"
        await query.edit_message_text(
            f"Enter the new monthly budget for {selected_category}:"
        )
    elif data.startswith("delete_"):
        selected_category = data.replace("delete_", "")
        await delete_selected_category(query, context, selected_category)

    elif data == "view_category":
        # Handle view categories (this can be expanded as needed)
        await view_category_handler(query, context)

    elif data == "add_category":
        # Handle add category
        await add_category_handler(query, context)

    elif data == "edit_category":
        # Show categories for editing
        await edit_category_handler(query, context)

    elif data == "delete_category":
        # Show categories for deletion
        await delete_category_handler(query, context)

    else:
        # Fallback for unrecognized data
        await query.edit_message_text("Unknown action. Please try again.")


async def handle_general_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    General message handler for other text messages.
    """
    text = update.message.text
    if text.lower() in ("hi", "hello"):
        await update.message.reply_text("Hello! How can I assist you today?")
    else:
        await update.message.reply_text(
            "Sorry, I didn't understand that. Please use /help to see available commands."
        )


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
    app.add_handler(CallbackQueryHandler(unified_callback_query_handler))
    
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.ChatType.PRIVATE, combined_message_handler
        )
    )
    app.add_handler(MessageHandler(filters.COMMAND, fallback_command))
    app.add_error_handler(error)
    print("Polling..")
    app.run_polling(poll_interval=3)
