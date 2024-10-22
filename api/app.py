"""
This module defines the main FastAPI application for Money Manager.
"""

import uvicorn
from fastapi import FastAPI

from api.routers import expenses, users

app = FastAPI()

# Include routers for different functionalities
app.include_router(expenses.router)
app.include_router(users.router)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Handles the shutdown event to close the MongoDB client.
    """
    # Call the shutdown function for MongoDB client
    await users.shutdown_db_client()


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
