# user.py
from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from typing import Optional
import datetime
from api.config import MONGO_URI
from bson import ObjectId

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

router = APIRouter(prefix="/users", tags=["Users"])

# MongoDB setup
client = AsyncIOMotorClient(MONGO_URI)
db = client.mmdb
users_collection = db.users
tokens_collection = db.tokens
accounts_collection = db.accounts

# Model for creating a user
class UserCreate(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    password: Optional[str] = None
    categories: Optional[list] = None
    currencies: Optional[list] = None

def format_id(document):
    document["_id"] = str(document["_id"])
    return document

# Function to create an access token
def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.UTC) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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

# Endpoint to create a demo user
@router.post("/")
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
        "categories": default_categories,
        "currencies": default_currencies
    }
    result = await users_collection.insert_one(user_data)
    user_id = result.inserted_id
    if not user_id:
        raise HTTPException(status_code=500, detail="Failed to create user")

    # Create default accounts for the user
    default_accounts = [
        {"user_id": str(user_id), "account_type": "Checking", "balance": 1000.0, "currency": "USD"},
        {"user_id": str(user_id), "account_type": "Savings", "balance": 5000.0, "currency": "USD"}
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
        {"user_id": str(user["_id"]), "token": access_token, "expires_at": datetime.datetime.now(datetime.UTC) + access_token_expires, "token_type": "bearer"},
    )

    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint to get user details
@router.get("/")
async def get_user_details(token: str = Depends(oauth2_scheme)):
    user_id = verify_token(token)
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return format_id(user)

@router.put("/")
async def update_user_details(user_update: UserUpdate, token: str = Depends(oauth2_scheme)):
    user_id = verify_token(token)
    update_fields = user_update.dict(exclude_unset=True)
    existing_user = await users_collection.find_one({"_id": ObjectId(user_id)})

    if "password" in update_fields and update_fields["password"]:
        # In a real application, you should hash the password
        update_fields["password"] = update_fields["password"]

    if "categories" in update_fields and isinstance(update_fields["categories"], list):
        new_categories = list(set(existing_user.get("categories", []) + update_fields["categories"]))
        update_fields["categories"] = new_categories

    if "currencies" in update_fields and isinstance(update_fields["currencies"], list):
        new_currencies = list(set(existing_user.get("currencies", []) + update_fields["currencies"]))
        update_fields["currencies"] = new_currencies

    result = await users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_fields})
    if result.modified_count == 1:
        updated_user = await users_collection.find_one({"_id": ObjectId(user_id)})
        return {"message": "User updated successfully", "updated_user": format_id(updated_user)}
    else:
        raise HTTPException(status_code=500, detail="Failed to update user")

# Endpoint to delete a user
@router.delete("/")
async def delete_user(token: str = Depends(oauth2_scheme)):
    user_id = verify_token(token)
    # Delete user tokens
    await tokens_collection.delete_many({"user_id": user_id})
    # Delete user accounts
    await accounts_collection.delete_many({"user_id": user_id})
    # Delete user
    result = await users_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 1:
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete user")