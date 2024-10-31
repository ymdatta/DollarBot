# import base64
# import io
# from typing import List

# import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd
# from fastapi import APIRouter, Header, HTTPException, Query
# from fastapi.responses import HTMLResponse
# from motor.motor_asyncio import AsyncIOMotorClient
# from pydantic import BaseModel
# from pymongo import MongoClient

# from api.config import MONGO_URI
# from api.utils.auth import verify_token

# # MongoDB setup
# client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URI)
# db = client.mmdb
# expenses_collection = db.expenses
# accounts_collection = db.accounts

# router = APIRouter(prefix="/analytics", tags=["Analytics"])


# # Fetches expense data from MongoDB and returns a DataFrame
# async def get_expense_data():
#     cursor = expenses_collection.find()  # Corrected collection reference
#     expenses = await cursor.to_list(length=1000)  # Adjust limit as needed
#     expenses_df = pd.DataFrame(expenses)
#     return expenses_df


# # Generates custom visualization based on user inputs
# def create_custom_visualization(expenses_df, x_var, y_var, graph_type):
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
#         ax.axis("equal")  # Ensures pie chart is circular

#     ax.set_title(f"{graph_type.capitalize()} Chart of {y_var} by {x_var}")
#     ax.set_xlabel(x_var)
#     ax.set_ylabel(y_var)
#     plt.tight_layout()

#     buf = io.BytesIO()
#     plt.savefig(buf, format="png")
#     plt.close(fig)
#     buf.seek(0)
#     return base64.b64encode(buf.getvalue()).decode("utf-8")


# # API endpoint for generating and returning a custom visualization
# @router.get("/analytics", response_class=HTMLResponse)
# async def get_analytics(
#     x_var: str = Query(
#         "date", title="X-axis variable", enum=["date", "category"]
#     ),  # Use correct column names
#     y_var: str = Query(
#         "amount", title="Y-axis variable", enum=["amount"]
#     ),  # Use correct column names
#     graph_type: str = Query(
#         "line", title="Graph type", enum=["line", "bar", "pie"]
#     ),  # Dropdown for graph type
# ):
#     # Fetch data from MongoDB
#     expenses_df = await get_expense_data()

#     # Validate graph type
#     valid_graph_types = ["line", "bar", "pie"]
#     if graph_type not in valid_graph_types:
#         raise HTTPException(status_code=422, detail="Invalid graph type")

#     # Validate x_var and y_var against DataFrame columns
#     if x_var not in expenses_df.columns or y_var not in expenses_df.columns:
#         raise HTTPException(status_code=422, detail="Invalid x or y variable")

#     image_data = create_custom_visualization(expenses_df, x_var, y_var, graph_type)
#     html_content = f"""
#     <html>
#         <head>
#             <title>Custom Expense Analytics</title>
#         </head>
#         <body>
#             <h1>Custom Expense Analytics Visualization</h1>
#             <img src="data:image/png;base64,{image_data}" alt="Custom Visualization">
#         </body>
#     </html>
#     """
#     return HTMLResponse(content=html_content)
