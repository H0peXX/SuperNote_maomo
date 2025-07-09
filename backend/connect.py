from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# MongoDB URI
uri = "mongodb+srv://chakritmesupphaisan:admin@cluster0.qcym40v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to the client
client = MongoClient(uri, server_api=ServerApi('1'))

# Confirm connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("Connection failed:", e)

# --- READ DATA ---

# Select database and collection
db = client["maomo"]  # Change this
collection = db["users"]  # Change this

# Example: Find one document
document = collection.find_one()
print("One document:", document.get("username"))

# Example: Find many documents
for doc in collection.find():
    print(doc.get("username"))

# Example: Find with filter
query = {"name": "lnwza"}
results = collection.find(query)
for doc in results:
    print("Filtered:", doc.get("username"))
