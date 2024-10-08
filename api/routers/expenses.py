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
from ..config import MONGO_URI
from fastapi import Header
from rich import inspect
# Constants for authentication
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        print(payload)
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
        {"user_id": str(user_id), "account_type": "Checking", "balance": 1000.0},
        {"user_id": str(user_id), "account_type": "Savings", "balance": 5000.0}
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

# Endpoint to add a new expense
@router.post("/add/")
async def add_expense(amount: float, currency: str, category: str, description: str = None, account_type: str = "Checking", token: str = Header(None)):
    user_id = verify_token(token)
    account = await accounts_collection.find_one({"user_id": user_id, "account_type": account_type})
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    print(user)
    inspect(user_id)
    if not account:
        raise HTTPException(status_code=400, detail="Invalid account type")

    if account["balance"] < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance in {} account".format(account_type))
    
    currency = currency.upper()
    if currency not in user["currencies"]:
        raise HTTPException(status_code=400, detail=f"Currency type is not added to user account. Available currencies are {user['currencies']}")
    
    if category not in user["categories"]:
        raise HTTPException(status_code=400, detail=f"Category is not present in the user account. Available categories are {user['categories']}")

    # Deduct amount from user's account balance
    new_balance = account["balance"] - amount
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
        return {"message": "Expense added successfully", "expense": format_id(expense), "new_balance":new_balance}
    else:
        raise HTTPException(status_code=500, detail="Failed to add expense")

# Endpoint to get all expenses for a user
@router.get("/")
async def get_expenses(token: str = Depends(oauth2_scheme)):
    user_id = verify_token(token)
    expenses = await expenses_collection.find({"user_id": user_id}).to_list(1000)
    return {"expenses": [format_id(expense) for expense in expenses]}

# Endpoint to delete an expense by ID
@router.delete("/delete/{expense_id}")
async def delete_expense(expense_id: str, token: str = Depends(oauth2_scheme)):
    user_id = verify_token(token)
    expense = await expenses_collection.find_one({"_id": ObjectId(expense_id)})
    if not expense or expense["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Expense not found")

    account_type = expense["account_type"]
    amount = expense["amount"]

    # Refund the amount to user's account
    account = await accounts_collection.find_one({"user_id": user_id, "account_type": account_type})
    new_balance = account["balance"] + amount
    await accounts_collection.update_one({"_id": account["_id"]}, {"$set": {"balance": new_balance}})

    # Delete the expense
    result = await expenses_collection.delete_one({"_id": ObjectId(expense_id)})

    if result.deleted_count == 1:
        return {"message": "Expense deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete expense")

# Endpoint to update an expense by ID
@router.put("/update/{expense_id}")
async def update_expense(expense_id: str, amount: float = None, category: str = None, description: str = None, token: str = Depends(oauth2_scheme)):
    user_id = verify_token(token)
    expense = await expenses_collection.find_one({"_id": ObjectId(expense_id)})
    if not expense or expense["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Expense not found")

    update_fields = {}
    if amount is not None:
        update_fields["amount"] = amount
        account_type = expense["account_type"]
        account = await accounts_collection.find_one({"user_id": user_id, "account_type": account_type})
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Adjust the user's balance
        original_amount = expense["amount"]
        difference = amount - original_amount
        if account["balance"] < difference:
            raise HTTPException(status_code=400, detail="Insufficient balance to update the expense")
        new_balance = account["balance"] - difference
        await accounts_collection.update_one({"_id": account["_id"]}, {"$set": {"balance": new_balance}})

    if category is not None:
        update_fields["category"] = category
    if description is not None:
        update_fields["description"] = description

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await expenses_collection.update_one({"_id": ObjectId(expense_id)}, {"$set": update_fields})
    if result.modified_count == 1:
        updated_expense = await expenses_collection.find_one({"_id": ObjectId(expense_id)})
        return {"message": "Expense updated successfully", "updated_expense": format_id(updated_expense)}
    else:
        raise HTTPException(status_code=500, detail="Failed to update expense")