from pymongo import MongoClient

# TODO: move this to .env file at some point
# tried using python-dotenv but kept getting ModuleNotFoundError
# just hardcoding for now, works fine locally
MONGO_URI = "mongodb://localhost:27017"

client = MongoClient(MONGO_URI)

db = client["order_management"]
