"""
This module defines the main FastAPI application for Money Manager.
"""

import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.routers import expenses, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    # You can add startup logic here if needed
    yield
    # Handles the shutdown event to close the MongoDB client
    await users.shutdown_db_client()

app = FastAPI(lifespan=lifespan)

# Include routers for different functionalities
app.include_router(expenses.router)
app.include_router(users.router)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
