# expenses.py
from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os
import datetime
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
from .config import MONGO_URI
from fastapi import Header
from rich import inspect
from forex_python.converter import CurrencyRates
from currency_converter import CurrencyConverter

currency_converter = CurrencyConverter()

# Constants for authentication
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30*24*60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

router = APIRouter(prefix="/expenses", tags=["Expenses"])

# MongoDB setup
client = AsyncIOMotorClient(MONGO_URI)
db = client.mmdb
users_collection = db.users
tokens_collection = db.tokens
expenses_collection = db.expenses
accounts_collection = db.accounts

def format_id(document):
    document["_id"] = str(document["_id"])
    return document

def verify_token(token: str):
    if token is None:
        raise HTTPException(status_code=401, detail="Token is missing")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="User not found")
        token_exists = tokens_collection.find_one({"user_id": user_id, "token": token})
        if not token_exists:
            raise HTTPException(status_code=401, detail="Token does not exist")
        return user_id
    except JWTError as e:
        if "Signature has expired" in str(e):
            tokens_collection.delete_one({"token": token})
            raise HTTPException(status_code=401, detail="Token has expired")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Model for creating a user
class UserCreate(BaseModel):
    username: str
    password: str

# Endpoint to create a demo user
@router.post("/create_user/")
async def create_user(user: UserCreate):
    # Check if the user already exists
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    default_categories = ["Food", "Groceries", "Utilities", "Transport", "Shopping", "Miscellaneous"]
    default_currencies = ["USD", "INR", "GBP", "EUR"]

    # Insert the new user
    user_data = {
        "username": user.username,
        "password": user.password,  # In a real application, you should hash the password
        "categories":default_categories,
        "currencies":default_currencies
    }
    result = await users_collection.insert_one(user_data)
    user_id = result.inserted_id
    if not user_id:
        raise HTTPException(status_code=500, detail="Failed to create user")

    # Create default accounts for the user
    default_accounts = [
        {"user_id": str(user_id), "account_type": "Checking", "balance": 1000.0, "currency":"USD"},
        {"user_id": str(user_id), "account_type": "Savings", "balance": 5000.0, "currency":"USD"}
    ]
    
    await accounts_collection.insert_many(default_accounts)

    return {"message": "User and default accounts created successfully"}

# Endpoint to generate a token for a user
@router.post("/token/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), token_expires: Optional[int] = ACCESS_TOKEN_EXPIRE_MINUTES):
    user = await users_collection.find_one({"username": form_data.username})
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token_expires = datetime.timedelta(minutes=token_expires)
    access_token = create_access_token(data={"sub": str(user["_id"]), "username": user["username"]}, expires_delta=access_token_expires)

    # Save the token in the database
    await tokens_collection.insert_one(
        {"user_id": str(user["_id"]), "token": access_token, "expires_at": datetime.datetime.utcnow() + access_token_expires, "token_type": "bearer"}, )

    return {"access_token": access_token, "token_type": "bearer"}

# Function to create an access token
def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def convert_currency(amount, from_cur, to_cur):
    if from_cur == to_cur:
        return amount
    try:
        return currency_converter.convert(amount, from_cur, to_cur)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Currency conversion failed: {str(e)}")

# Endpoint to add a new expense
@router.post("/add/")
async def add_expense(amount: float, currency: str, category: str, description: str = None, account_type: str = "Checking", token: str = Header(None)):
    user_id = verify_token(token)
    account = await accounts_collection.find_one({"user_id": user_id, "account_type": account_type})
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not account:
        raise HTTPException(status_code=400, detail="Invalid account type")

    currency = currency.upper()
    if currency not in user["currencies"]:
        raise HTTPException(status_code=400, detail=f"Currency type is not added to user account. Available currencies are {user['currencies']}")
    converted_amount = convert_currency(amount, currency, account["currency"])
    
    if account["balance"] < converted_amount:
        raise HTTPException(status_code=400, detail="Insufficient balance in {} account".format(account_type))
    
    if category not in user["categories"]:
        raise HTTPException(status_code=400, detail=f"Category is not present in the user account. Available categories are {user['categories']}")

    # Deduct amount from user's account balance
    new_balance = account["balance"] - converted_amount
    await accounts_collection.update_one({"_id": account["_id"]}, {"$set": {"balance": new_balance}})

    # Record the expense
    expense = {
        "user_id": user_id,
        "amount": amount,
        "currency": currency,
        "category": category,
        "description": description,
        "account_type": account_type,
        "date": datetime.datetime.now()
    }
    result = await expenses_collection.insert_one(expense)

    if result.inserted_id:
        return {"message": "Expense added successfully", "expense": format_id(expense), "balance":new_balance}
    else:
        raise HTTPException(status_code=500, detail="Failed to add expense")

# Endpoint to get all expenses for a user
@router.get("/")
async def get_expenses(token: str = Header(None)):
    user_id = verify_token(token)
    expenses = await expenses_collection.find({"user_id": user_id}).to_list(1000)
    return {"expenses": [format_id(expense) for expense in expenses]}

# Endpoint to delete an expense by ID
@router.delete("/delete/{expense_id}")
async def delete_expense(expense_id: str, token: str = Header(None)):
    user_id = verify_token(token)
    try:
        expense = await expenses_collection.find_one({"_id": ObjectId(expense_id)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve the expense: {str(e)}")

    if not expense:
        raise HTTPException(status_code=404, detail=f"Expense with ID {expense_id} not found.")

    if expense["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this expense.")

    account_type = expense["account_type"]
    try:
        account = await accounts_collection.find_one({"user_id": user_id, "account_type": account_type})
        if not account:
            raise HTTPException(status_code=404, detail=f"Account of type '{account_type}' not found for user.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve account information: {str(e)}")

    try:
        amount = convert_currency(expense["amount"], expense["currency"], account["currency"])
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=f"Failed to convert currency: {e.detail}")

    # Refund the amount to user's account
    new_balance = account["balance"] + amount
    try:
        await accounts_collection.update_one({"_id": account["_id"]}, {"$set": {"balance": new_balance}})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update account balance: {str(e)}")

    # Delete the expense
    result = await expenses_collection.delete_one({"_id": ObjectId(expense_id)})
    if result.deleted_count == 1:
        return {"message": "Expense deleted successfully", "balance": new_balance}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete expense from the database.")

# Endpoint to update an expense by ID
@router.put("/update/{expense_id}")
async def update_expense(expense_id: str, amount: float = None, currency: str = None, category: str = None, description: str = None, token: str = Header(None)):
    user_id = verify_token(token)
    try:
        expense = await expenses_collection.find_one({"_id": ObjectId(expense_id)})
        if not expense:
            raise HTTPException(status_code=404, detail=f"Expense with ID {expense_id} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve the expense: {str(e)}")

    if expense["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this expense.")

    account_type = expense["account_type"]
    try:
        account = await accounts_collection.find_one({"user_id": user_id, "account_type": account_type})
        if not account:
            raise HTTPException(status_code=404, detail=f"Account of type '{account_type}' not found for user.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve account information: {str(e)}")

    update_fields = {}
    if amount is not None:
        try:
            original_amount_converted = convert_currency(expense["amount"], expense["currency"], account["currency"])
            new_amount_converted = convert_currency(amount, currency or expense["currency"], account["currency"])
        except HTTPException as e:
            raise HTTPException(status_code=400, detail=f"Failed to convert currency for amount update: {e.detail}")

        difference = new_amount_converted - original_amount_converted
        new_balance = account["balance"] - difference

        if new_balance < 0:
            raise HTTPException(status_code=400, detail="Insufficient balance to update the expense.")

        try:
            await accounts_collection.update_one({"_id": account["_id"]}, {"$set": {"balance": new_balance}})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update account balance: {str(e)}")

        update_fields["amount"] = amount

    if currency is not None:
        currency = currency.upper()
        if currency not in user["currencies"]:
            raise HTTPException(status_code=400, detail=f"Currency type '{currency}' is not added to user account. Available currencies are {user['currencies']}")
        update_fields["currency"] = currency

    if category is not None:
        if category not in user["categories"]:
            raise HTTPException(status_code=400, detail=f"Category '{category}' is not present in the user account. Available categories are {user['categories']}")
        update_fields["category"] = category

    if description is not None:
        update_fields["description"] = description

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update.")

    try:
        result = await expenses_collection.update_one({"_id": ObjectId(expense_id)}, {"$set": update_fields})
        if result.modified_count == 1:
            updated_expense = await expenses_collection.find_one({"_id": ObjectId(expense_id)})
            return {"message": "Expense updated successfully", "updated_expense": format_id(updated_expense), "balance": new_balance}
        else:
            raise HTTPException(status_code=500, detail="Failed to update expense in the database.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update expense: {str(e)}")

    user_id = verify_token(token)
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    try:
        expense = await expenses_collection.find_one({"_id": ObjectId(expense_id)})
    except:
        raise HTTPException(status_code=404, detail="Expense could not be retrieved")
    if not expense or expense["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Expense not found")

    update_fields = {}

    if currency is not None:
        currency = currency.upper()
        if currency not in user["currencies"]:
            raise HTTPException(status_code=400, detail=f"Currency type is not added to user account. Available currencies are {user['currencies']}")
        elif currency is not None:
            update_fields["currency"] = currency

    account_type = expense["account_type"]
    account = await accounts_collection.find_one({"user_id": user_id, "account_type": account_type})
    if amount is not None:
        update_fields["amount"] = amount
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Adjust the user's balance
        # Convert old and new amounts to the account currency to determine balance adjustment
        original_amount_converted = convert_currency(expense["amount"], expense["currency"], account["currency"])
        new_amount_converted = convert_currency(amount, currency or expense["currency"], account["currency"])
        
        difference = new_amount_converted - original_amount_converted
        new_balance = account["balance"] - difference

        if new_balance < 0:
            raise HTTPException(status_code=400, detail="Insufficient balance to update the expense")
        await accounts_collection.update_one({"_id": account["_id"]}, {"$set": {"balance": new_balance}})

    
    if category is not None:
        if category not in user["categories"]:
            raise HTTPException(status_code=400, detail=f"Category is not present in the user account. Available categories are {user['categories']}")
        elif category is not None:
            update_fields["category"] = category
        
    if description is not None:
        update_fields["description"] = description

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await expenses_collection.update_one({"_id": ObjectId(expense_id)}, {"$set": update_fields})
    if result.modified_count == 1:
        updated_expense = await expenses_collection.find_one({"_id": ObjectId(expense_id)})
        return {"message": "Expense updated successfully", "updated_expense": format_id(updated_expense), "balance":new_balance}
    else:
        raise HTTPException(status_code=500, detail="Failed to update expense")