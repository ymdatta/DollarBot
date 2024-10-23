"""
This module defines the main FastAPI application for Money Manager.
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api.routers import accounts, expenses, users


@asynccontextmanager
async def lifespan():
    """Lifespan"""
    yield
    # Handles the shutdown event to close the MongoDB client
    await users.shutdown_db_client()


app = FastAPI(lifespan=lifespan)

# Include routers for different functionalities
app.include_router(users.router)
app.include_router(accounts.router)
app.include_router(expenses.router)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
