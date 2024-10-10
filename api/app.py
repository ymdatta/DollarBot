# app.py
from fastapi import FastAPI
from api.routers import expenses, users
import uvicorn
import asyncio

app = FastAPI()

# # Include routers for different functionalities
app.include_router(expenses.router)
app.include_router(users.router)
# app.include_router(budgets.router)


@app.on_event("shutdown")
async def shutdown_event():
    # Call the shutdown function for MongoDB client
    await users.shutdown_db_client()


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)