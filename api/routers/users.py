"""
This module provides user-related API routes for the Money Manager application.
"""

import datetime
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pydantic import BaseModel

from api.config import MONGO_URI, TOKEN_ALGORITHM, TOKEN_SECRET_KEY

ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

router = APIRouter(prefix="/users", tags=["Users"])

# MongoDB setup
client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URI)
db = client.mmdb
users_collection = db.users
tokens_collection = db.tokens
accounts_collection = db.accounts
expenses_collection = db.expenses


class UserCreate(BaseModel):
    """Schema for creating a user."""

    username: str
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    password: Optional[str] = None
    categories: Optional[list] = None
    currencies: Optional[list] = None


def format_id(document):
    """Format the MongoDB document ID to string."""
    document["_id"] = str(document["_id"])
    return document


def create_access_token(data: dict, expires_delta: datetime.timedelta):
    """Create an access token with an expiration time."""
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.UTC) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, TOKEN_SECRET_KEY, algorithm=TOKEN_ALGORITHM)
    return encoded_jwt


async def verify_token(token: str):
    """Verify the validity of an access token."""
    if token is None:
        raise HTTPException(status_code=401, detail="Token is missing")
    try:
        payload = jwt.decode(token, TOKEN_SECRET_KEY, algorithms=[TOKEN_ALGORITHM])
        user_id = payload.get("sub")
        token_exists = await tokens_collection.find_one(
            {"user_id": user_id, "token": token}
        )
        if not token_exists:
            raise HTTPException(status_code=401, detail="Token does not exist")
        return user_id
    except JWTError as e:
        if "Signature has expired" in str(e):
            await tokens_collection.delete_one({"token": token})
            raise HTTPException(status_code=401, detail="Token has expired") from e
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        ) from e


@router.post("/")
async def create_user(user: UserCreate):
    """Create a new user along with default accounts."""
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    if not user.username or not user.password:
        raise HTTPException(status_code=422, detail="Invalid credential")

    default_categories = [
        "Food",
        "Groceries",
        "Utilities",
        "Transport",
        "Shopping",
        "Miscellaneous",
    ]
    default_currencies = ["USD", "INR", "GBP", "EUR"]

    # Insert the new user
    user_data = {
        "username": user.username,
        "password": user.password,  # In a real application, you should hash the password
        "categories": default_categories,
        "currencies": default_currencies,
    }
    result = await users_collection.insert_one(user_data)
    user_id = result.inserted_id
    if not user_id:
        raise HTTPException(status_code=500, detail="Failed to create user")

    # Create default accounts for the user
    default_accounts = [
        {
            "user_id": str(user_id),
            "account_type": "Checking",
            "balance": 1000.0,
            "currency": "USD",
        },
        {
            "user_id": str(user_id),
            "account_type": "Savings",
            "balance": 5000.0,
            "currency": "USD",
        },
    ]

    await accounts_collection.insert_many(default_accounts)

    return {"message": "User and default accounts created successfully"}


@router.get("/")
async def get_user(token: str = Header(None)):
    """Get user details."""
    user_id = await verify_token(token)
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return format_id(user)


@router.put("/")
async def update_user(user_update: UserUpdate, token: str = Header(None)):
    """Update user information such as password, categories, or currencies."""
    user_id = await verify_token(token)
    update_fields = user_update.dict(exclude_unset=True)
    existing_user: AsyncIOMotorCollection = await users_collection.find_one(
        {"_id": ObjectId(user_id)}
    )

    if "password" in update_fields and update_fields["password"]:
        # In a real application, you should hash the password
        update_fields["password"] = update_fields["password"]

    if "categories" in update_fields and isinstance(update_fields["categories"], list):
        new_categories = list(
            set(existing_user.get("categories", []) + update_fields["categories"])
        )
        update_fields["categories"] = new_categories

    if "currencies" in update_fields and isinstance(update_fields["currencies"], list):
        new_currencies = list(
            set(existing_user.get("currencies", []) + update_fields["currencies"])
        )
        update_fields["currencies"] = new_currencies
    try:
        result = await users_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_fields}
        )
        if result.modified_count == 1:
            updated_user = await users_collection.find_one({"_id": ObjectId(user_id)})
            return {
                "message": "User updated successfully",
                "updated_user": format_id(updated_user),
            }
        raise HTTPException(status_code=400, detail="Nothing to modify")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update user") from e


@router.delete("/")
async def delete_user(token: str = Header(None)):
    """Delete a user and all associated accounts, tokens, and expenses."""
    user_id = await verify_token(token)
    await tokens_collection.delete_many({"user_id": user_id})
    await accounts_collection.delete_many({"user_id": user_id})
    await expenses_collection.delete_many({"user_id": user_id})
    result = await users_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 1:
        return {"message": "User deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete user")


@router.post("/token/")
async def create_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    token_expires: float = ACCESS_TOKEN_EXPIRE_MINUTES,
):
    """Create an access token for a user."""
    user = await users_collection.find_one({"username": form_data.username})
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token_expires = datetime.timedelta(minutes=token_expires)
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "username": user["username"]},
        expires_delta=access_token_expires,
    )

    await tokens_collection.insert_one(
        {
            "user_id": str(user["_id"]),
            "token": access_token,
            "expires_at": datetime.datetime.now(datetime.UTC) + access_token_expires,
            "token_type": "bearer",
        },
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/token/")
async def get_token(token: str = Header(None)):
    """Get current token details."""
    user_id = await verify_token(token)
    token_data = await tokens_collection.find_one({"user_id": user_id, "token": token})
    return format_id(token_data)


@router.put("/token/")
async def update_token(token_expires: int, token: str = Header(None)):
    """Update the expiration time for the current token."""
    user_id = await verify_token(token)
    updated_expiry = datetime.timedelta(minutes=token_expires)
    new_expiry_time = datetime.datetime.now(datetime.UTC) + updated_expiry

    result = await tokens_collection.update_one(
        {"user_id": user_id, "token": token}, {"$set": {"expires_at": new_expiry_time}}
    )
    if result.modified_count == 1:
        return {"message": "Token expiration updated successfully"}
    raise HTTPException(status_code=500, detail="Failed to update token expiration")


@router.delete("/token/")
async def delete_token(token_to_delete: str, token: str = Header(None)):
    """Delete a specific token."""
    user_id = await verify_token(token)
    result = await tokens_collection.delete_one(
        {"user_id": user_id, "token": token_to_delete}
    )
    if result.deleted_count == 1:
        return {"message": "Token deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete token")


@router.on_event("shutdown")
async def shutdown_db_client():
    """Shutdown event for MongoDB client."""
    client.close()
