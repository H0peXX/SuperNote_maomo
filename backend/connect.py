from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Get credentials from .env
user = os.getenv("MONGODB_USER")
password = os.getenv("MONGODB_PASSWORD")

# MongoDB URI with credentials
uri = f"mongodb+srv://{user}:{password}@cluster0.qcym40v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to the client
client = MongoClient(uri, server_api=ServerApi('1'))

# Confirm connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("Connection failed:", e)

# --- READ DATA ---
db = client["maomo"]
collection = db["users"]

# Example: Find one document
document = collection.find_one()
if document:
    print("One document:", document.get("username"))

# Example: Find many documents
for doc in collection.find():
    print(doc.get("username"))

# Example: Find with filter
query = {"name": "lnwza"}
results = collection.find(query)
for doc in results:
    print("Filtered:", doc.get("username"))
