# expenses.py
from fastapi import APIRouter, HTTPException, Depends, Header
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from api.config import MONGO_URI
from . import users
from currency_converter import CurrencyConverter
import datetime

currency_converter = CurrencyConverter()

router = APIRouter(prefix="/expenses", tags=["Expenses"])

# MongoDB setup
client = AsyncIOMotorClient(MONGO_URI)
db = client.mmdb
users_collection = db.users
expenses_collection = db.expenses
accounts_collection = db.accounts

def format_id(document):
    document["_id"] = str(document["_id"])
    return document

def convert_currency(amount, from_cur, to_cur):
    if from_cur == to_cur:
        return amount
    try:
        return currency_converter.convert(amount, from_cur, to_cur)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Currency conversion failed: {str(e)}")

# Endpoint to add a new expense
@router.post("/")
async def add_expense(amount: float, currency: str, category: str, description: str = None, account_type: str = "Checking", token: str = Header(None)):
    user_id = user.verify_token(token)
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
        "date": datetime.datetime.now(datetime.UTC)
    }
    result = await expenses_collection.insert_one(expense)

    if result.inserted_id:
        return {"message": "Expense added successfully", "expense": format_id(expense), "balance":new_balance}
    else:
        raise HTTPException(status_code=500, detail="Failed to add expense")

# Endpoint to get all expenses for a user
@router.get("/")
async def get_expenses(token: str = Header(None)):
    user_id = users.verify_token(token)
    expenses = await expenses_collection.find({"user_id": user_id}).to_list(1000)
    return {"expenses": [format_id(expense) for expense in expenses]}

# Endpoint to delete an expense by ID
@router.delete("/{expense_id}")
async def delete_expense(expense_id: str, token: str = Header(None)):
    user_id = users.verify_token(token)
    try:
        expense = await expenses_collection.find_one({"_id": ObjectId(expense_id)})
    except:
        raise HTTPException(status_code=404, detail="Expense could not be retrieved")

    if not expense or expense["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Expense not found")

    account_type = expense["account_type"]
    account = await accounts_collection.find_one({"user_id": user_id, "account_type": account_type})
    amount = convert_currency(expense["amount"], expense["currency"], account["currency"])

    # Refund the amount to user's account
    new_balance = account["balance"] + amount
    await accounts_collection.update_one({"_id": account["_id"]}, {"$set": {"balance": new_balance}})

    # Delete the expense
    result = await expenses_collection.delete_one({"_id": ObjectId(expense_id)})

    if result.deleted_count == 1:
        return {"message": "Expense deleted successfully", "balance":new_balance}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete expense")

# Endpoint to update an expense by ID
@router.put("/{expense_id}")
async def update_expense(expense_id: str, amount: float = None, currency: str = None, category: str = None, description: str = None, token: str = Header(None)):
    user_id = user.verify_token(token)
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