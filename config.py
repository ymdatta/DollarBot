"""
This module contains configuration settings for the Money Manager application.
"""

import os

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://mmdb_admin:tiaNSKxzyO2NdXts@moneymanagerdb.s2bp9.mongodb.net/"
    "?retryWrites=true&w=majority&appName=MoneyManagerDB",
)

TOKEN_SECRET_KEY = "your_secret_key"
TOKEN_ALGORITHM = "HS256"

API_BIND_HOST = "0.0.0.0"
API_BIND_PORT = 9999

TELEGRAM_BOT_TOKEN = "7217139754:AAGTo4BtF2obYrxm_MsHmXLekxvnNQ8F3fs"
TELEGRAM_BOT_API_BASE_URL = "http://localhost:9999"
