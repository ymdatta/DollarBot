import io

import pandas as pd
from bson import ObjectId  # Make sure to import ObjectId if you are using it
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from api.config import MONGO_URI
from api.routers.accounts import accounts_collection  # Import the accounts collection
from api.routers.expenses import expenses_collection
from api.utils.auth import verify_token  # Import your authentication function

router = APIRouter(prefix="/export", tags=["export"])

# MongoDB setup
client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URI)
db = client.mmdb
accounts_collection = db.accounts


async def get_account_details(account_id: str, user_id: str):
    """
    Fetch the account expenses and balance for a specific account.

    Args:
        account_id (str): The account ID.
        user_id (str): The user ID.

    Returns:
        pd.DataFrame: A DataFrame containing expenses data.
        float: The balance of the account.
    """
    # Fetch the account to ensure it exists
    account = await accounts_collection.find_one(
        {"_id": ObjectId(account_id), "user_id": user_id}
    )

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Fetch expenses related to this account (assuming you have an expenses_collection)
    expenses = await expenses_collection.find({"account_id": account_id}).to_list(100)

    # Convert expenses to DataFrame
    if expenses:
        expenses_df = pd.DataFrame(expenses)
    else:
        expenses_df = pd.DataFrame()

    balance = account.get("balance", 0)

    return expenses_df, balance


@router.get("/export/csv/{account_id}")
async def export_expenses_to_csv(account_id: str, token: str = Header(None)):
    """Export account expenses to CSV format."""
    user_id = await verify_token(token)
    expenses, balance = await get_account_details(account_id, user_id)

    if expenses.empty:
        raise HTTPException(
            status_code=404, detail="No expenses found for this account."
        )

    csv_buffer = io.StringIO()
    expenses.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return StreamingResponse(
        iter([csv_buffer.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=expenses_{account_id}.csv"
        },
    )


@router.get("/export/pdf/{account_id}")
async def export_expenses_to_pdf(account_id: str, token: str = Header(None)):
    """Export account expenses to PDF format."""
    user_id = await verify_token(token)
    expenses, balance = await get_account_details(account_id, user_id)

    if expenses.empty:
        raise HTTPException(
            status_code=404, detail="No expenses found for this account."
        )

    pdf_buffer = io.BytesIO()
    pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=letter)
    pdf_canvas.drawString(100, 750, f"Expenses for Account ID: {account_id}")
    pdf_canvas.drawString(100, 730, f"Balance: {balance}")

    y = 700
    for index, row in expenses.iterrows():
        pdf_canvas.drawString(
            100, y, f"{row['date']} - {row['category']} - {row['amount']}"
        )
        y -= 20
        if y < 100:
            pdf_canvas.showPage()
            y = 750

    pdf_canvas.save()
    pdf_buffer.seek(0)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=expenses_{account_id}.pdf"
        },
    )
