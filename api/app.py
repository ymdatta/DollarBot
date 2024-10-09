# app.py
from fastapi import FastAPI
from api.routers import expenses, users
import uvicorn

app = FastAPI()

# # Include routers for different functionalities
app.include_router(expenses.router)
app.include_router(users.router)
# app.include_router(budgets.router)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)