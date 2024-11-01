"""
This module provides analytics endpoints for retrieving and visualizing
expense data. It includes routes to generate visualizations for expenses
from the last 7 days, the last one month, and by category.
"""

import base64
import io
from datetime import datetime, timedelta
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorClient

from api.config import MONGO_URI
from api.utils.auth import verify_token

# MongoDB setup
client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URI)
db = client.mmdb
expenses_collection = db.expenses
accounts_collection = db.accounts

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/expense/bar", response_class=HTMLResponse)
async def expense_bar(x_days:int, token:):
    ...

@router.get("/expense/pie", response_class=HTMLResponse)
async def expense_pie(x_days:int, token):
...

# # Helper function to fetch expense data from MongoDB and return a DataFrame
# async def get_expense_data(
#     user_id: str, date_filter: Optional[dict] = None
# ) -> pd.DataFrame:
#     """
#     Fetches expense data from MongoDB and returns it as a DataFrame.
#     """
#     query = date_filter if date_filter else {"user_id": user_id}  # Filter by user_id
#     cursor = expenses_collection.find(query)
#     expenses = await cursor.to_list(length=1000)
#     print(f"Fetched expenses: {expenses}")
#     return pd.DataFrame(expenses)


# # Function to create and return the custom visualization based on data and type
# def create_visualization(expenses_df, x_var, y_var, graph_type, title="") -> str:
#     """
#     Creates a visualization of expenses data and returns it as a base64-encoded PNG image.
#     """
#     fig, ax = plt.subplots(figsize=(10, 6))
#     if graph_type == "line":
#         ax.plot(expenses_df[x_var], expenses_df[y_var], marker="o")
#     elif graph_type == "bar":
#         ax.bar(expenses_df[x_var], expenses_df[y_var])
#     elif graph_type == "pie" and x_var == "category":
#         category_sums = expenses_df.groupby(x_var)[y_var].sum()
#         ax.pie(
#             category_sums, labels=category_sums.index, autopct="%1.1f%%", startangle=90
#         )
#         ax.axis("equal")

#     ax.set_title(title)
#     ax.set_xlabel(x_var)
#     ax.set_ylabel(y_var)
#     plt.tight_layout()

#     buf = io.BytesIO()
#     plt.savefig(buf, format="png")
#     plt.close(fig)
#     buf.seek(0)
#     return base64.b64encode(buf.getvalue()).decode("utf-8")


# # API endpoint for last 7 days expenses
# @router.get("/last-7-days", response_class=HTMLResponse)
# async def get_last_7_days_expenses(token: str = Header(None)):
#     try:
#         user_id = await verify_token(token)
#         date_filter = {
#             "date": {"$gte": datetime.now() - timedelta(days=7), "user_id": user_id}
#         }
#         expenses_df = await get_expense_data(user_id, date_filter)

#         if expenses_df.empty:
#             raise HTTPException(
#                 status_code=404, detail="No expenses found for the last 7 days"
#             )

#         image_data = create_visualization(
#             expenses_df,
#             x_var="date",
#             y_var="amount",
#             graph_type="line",
#             title="Last 7 Days Expenses",
#         )

#         return HTMLResponse(
#             content=f"""
#             <html>
#                 <head><title>Last 7 Days Expenses</title></head>
#                 <body>
#                     <h1>Last 7 Days Expenses</h1>
#                     <img src="data:image/png;base64,{image_data}" alt="Last 7 Days Expenses">
#                 </body>
#             </html>
#         """
#         )
#     except Exception as e:
#         print(f"Error: {e}")  # Log the error for debugging
#         raise HTTPException(status_code=500, detail="Internal Server Error")


# # API endpoint for last one month expenses
# @router.get("/last-one-month", response_class=HTMLResponse)
# async def get_last_one_month_expenses(token: str = Header(None)):
#     """
#     Returns an HTML response with a bar graph showing the expenses from the last month.
#     """
#     user_id = await verify_token(token)  # Verify the token to get the user_id
#     date_filter = {
#         "date": {"$gte": datetime.now() - timedelta(days=30), "user_id": user_id}
#     }
#     expenses_df = await get_expense_data(user_id, date_filter)
#     if expenses_df.empty:
#         raise HTTPException(
#             status_code=404, detail="No expenses found for the last one month"
#         )

#     image_data = create_visualization(
#         expenses_df,
#         x_var="date",
#         y_var="amount",
#         graph_type="bar",
#         title="Last One Month Expenses",
#     )
#     return HTMLResponse(
#         content=f"""
#         <html>
#             <head><title>Last One Month Expenses</title></head>
#             <body>
#                 <h1>Last One Month Expenses</h1>
#                 <img src="data:image/png;base64,{image_data}" alt="Last One Month Expenses">
#             </body>
#         </html>
#     """
#     )


# # API endpoint for category-wise expenses
# @router.get("/category-wise", response_class=HTMLResponse)
# async def get_category_wise_expenses(token: str = Header(None)):
#     """
#     Returns an HTML response with a pie chart showing expenses by category.
#     """
#     user_id = await verify_token(token)  # Verify the token to get the user_id
#     expenses_df = await get_expense_data(user_id)
#     if expenses_df.empty:
#         raise HTTPException(status_code=404, detail="No expenses found")

#     image_data = create_visualization(
#         expenses_df,
#         x_var="category",
#         y_var="amount",
#         graph_type="pie",
#         title="Category Wise Expenses",
#     )
#     return HTMLResponse(
#         content=f"""
#         <html>
#             <head><title>Category Wise Expenses</title></head>
#             <body>
#                 <h1>Category Wise Expenses</h1>
#                 <img src="data:image/png;base64,{image_data}" alt="Category Wise Expenses">
#             </body>
#         </html>
#     """
#     )
