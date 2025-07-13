from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask_cors import CORS
from dotenv import load_dotenv
import os
import bcrypt

# --- Flask + SQLAlchemy Setup ---
app = Flask(__name__)
CORS(app)
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

@app.route('/api/session', methods=['GET'])
def get_session():
    # For now, return no active session
    return jsonify({'user': None})

@app.route('/api/signup', methods=['POST', 'OPTIONS'])
def signup():
    if request.method == 'OPTIONS':
        return '', 200

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = user_collection.find_one({'username': username})
    if not user:
        return jsonify({'error': 'Invalid username or password'}), 401
        
    if bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({
            'user': {
                'username': user['username']
            }
        })
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

    # Check if user already exists
    if user_collection.find_one({'username': username}):
        return jsonify({'error': 'Username already exists'}), 400
    
    # Hash password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Create new user
    new_user = {
        'username': username,
        'password': hashed
    }
    user_collection.insert_one(new_user)
    
    return jsonify({'message': 'User created successfully'}), 201

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
