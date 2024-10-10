import os

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://mmdb_admin:tiaNSKxzyO2NdXts@moneymanagerdb.s2bp9.mongodb.net/?retryWrites=true&w=majority&appName=MoneyManagerDB",
)


TOKEN_SECRET_KEY = "your_secret_key"
TOKEN_ALGORITHM = "HS256"
