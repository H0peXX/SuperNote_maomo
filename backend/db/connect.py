from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()

# Debug: Check if environment variables are loaded
print(f"DEBUG: MONGODB_USER loaded: {'Yes' if os.getenv('MONGODB_USER') else 'No'}")
print(f"DEBUG: MONGODB_PASSWORD loaded: {'Yes' if os.getenv('MONGODB_PASSWORD') else 'No'}")
print(f"DEBUG: GENAI_API_KEY loaded: {'Yes' if os.getenv('GENAI_API_KEY') else 'No'}")
print(f"DEBUG: SECRET_KEY loaded: {'Yes' if os.getenv('SECRET_KEY') else 'No'}")

uri = f"mongodb+srv://{os.getenv('MONGODB_USER')}:{os.getenv('MONGODB_PASSWORD')}@cluster0.qcym40v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Connected to MongoDB.")
except Exception as e:
    print("MongoDB connection error:", e)

mongo_db = client["maomo"]
user_collection = mongo_db["users"]
team_collection = mongo_db["teams"]
member_collection = mongo_db["members"]
note_collection = mongo_db["notes"]
super_note_collection = mongo_db["supernotes"]

