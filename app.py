from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

# --- Flask + SQLAlchemy Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///supernote.db'
sql_db = SQLAlchemy(app)  # Avoid shadowing with MongoDB

# --- Load Environment Variables ---
load_dotenv()
user = os.getenv("MONGODB_USER")
password = os.getenv("MONGODB_PASSWORD")

# --- MongoDB Setup ---
uri = f"mongodb+srv://{user}:{password}@cluster0.qcym40v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("Connection failed:", e)

mongo_db = client["maomo"]
user_collection = mongo_db["users"]

# --- Routes ---
@app.route('/')
def home():
    return 'SuperNote Application'

@app.route('/calldata')
def calldata():
    document = user_collection.find_one()
    if document and "username" in document:
        return f"Username: {document['username']}"
    else:
        return "No user found or 'username' field missing.", 404

# --- Main ---
if __name__ == '__main__':
    app.run(debug=True)
