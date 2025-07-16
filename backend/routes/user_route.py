from flask import Blueprint, jsonify, request
from datetime import datetime
from db.connect import *
from flask_cors import CORS
import bcrypt
import jwt
import os
from flask_cors import cross_origin

# JWT settings
SECRET_KEY = f"{os.getenv('SECRET_KEY')}"  # Change this to a secure key in production
ALGORITHM = "HS256"



# Create blueprints for user, team, member, and note table routes
user_bp = Blueprint('user', __name__)
team_bp = Blueprint('team', __name__)
member_bp = Blueprint('member', __name__)
note_bp = Blueprint('note', __name__)


# Configure CORS for the blueprints
CORS(user_bp, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000", "http://localhost:5000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": [
            "Content-Type",
            "Authorization",
            "Access-Control-Allow-Origin",
            "Referer",
            "User-Agent",
            "sec-ch-ua",
            "sec-ch-ua-mobile",
            "sec-ch-ua-platform",
            "Sec-Fetch-Mode"
        ]
    }
})
CORS(team_bp, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000", "http://localhost:5000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": [
            "Content-Type",
            "Authorization",
            "Access-Control-Allow-Origin",
            "Referer",
            "User-Agent",
            "sec-ch-ua",
            "sec-ch-ua-mobile",
            "sec-ch-ua-platform",
            "Sec-Fetch-Mode"
        ]
    }
})
CORS(member_bp, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000", "http://localhost:5000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": [
            "Content-Type",
            "Authorization",
            "Access-Control-Allow-Origin",
            "Referer",
            "User-Agent",
            "sec-ch-ua",
            "sec-ch-ua-mobile",
            "sec-ch-ua-platform",
            "Sec-Fetch-Mode"
        ]
    }
})

# --- Get session status ---
@user_bp.route('/api/session', methods=['GET'])
def check_session():
    # Get the token from the Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'logged_in': False})
    
    token = auth_header.split(' ')[1]
    try:
        # Decode and verify the JWT token
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = decoded.get('sub')
        if username:
            return jsonify({'logged_in': True, 'username': username})
    except:
        pass
    
    return jsonify({'logged_in': False})

# --- Get first user (for test/demo) ---
@user_bp.route('/api/user', methods=['GET'])
def get_user():
    document = user_collection.find_one()
    if document and "username" in document:
        return jsonify({"username": document["username"]})
    else:
        return jsonify({"error": "No user found or 'username' field missing."}), 404


# --- Login route ---
@user_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = user_collection.find_one({'username': username})
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    # Compare password with hash in database
    stored_hash = user.get('password')
    if stored_hash and bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        # Create JWT token
        token = jwt.encode({"sub": user['username']}, SECRET_KEY, algorithm=ALGORITHM)
        return jsonify({
            'message': 'Login successful',
            'username': user['username'],
            'access_token': token,
            'token_type': 'Bearer'
        })
    else:
        return jsonify({'error': 'Invalid credentials'}), 401


# --- Signup route ---
@user_bp.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    fname = data.get('fname')
    lname = data.get('lname')
    email = data.get('email')
    dob = data.get('dob')  # Expecting string (e.g. 'YYYY-MM-DD')
    create_at = data.get('create_at')  # Optional ISO datetime string
    print("Received data:", data)

    if not username or not password or not email:
        return jsonify({'error': 'Username, password, and email are required'}), 400

    existing_user = user_collection.find_one({'username': username})
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 409

    # Parse DOB
    dob_date = None
    if dob:
        try:
            dob_date = datetime.strptime(dob, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'DOB must be in YYYY-MM-DD format'}), 400

    # Parse or set create_at
    if create_at:
        try:
            create_at_date = datetime.strptime(create_at, '%Y-%m-%dT%H:%M:%S')
        except Exception:
            create_at_date = datetime.utcnow()
    else:
        create_at_date = datetime.utcnow()

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    new_user = {
        'username': username,
        'password': hashed_password.decode('utf-8'),
        'first_name': fname,
        'last_name': lname,
        'email': email,
        'dob': dob_date,
        'create_at': create_at_date,
    }

    user_collection.insert_one(new_user)

    return jsonify({'message': 'User created successfully', 'username': username}), 201

# --- Create team route ---
@team_bp.route('/api/team', methods=['POST'])
def create_team():
    data = request.get_json()
    team_name = data.get('team_name')
    team_description = data.get('team_description')
    team_members = data.get('team_members', [])

    if not team_name or not team_description:
        return jsonify({'error': 'Team name and description are required'}), 400

    new_team = {
        'team_name': team_name,
        'team_description': team_description,
        'created_at': datetime.utcnow()
    }

    team_collection.insert_one(new_team)
    member_collection.insert_many([
        {'team_name': team_name, 'member_email': team_members} 
    ])

    return jsonify({
        'message': 'Team created successfully',
        'team_name': team_name,
        'team_description': team_description
    }), 201


# --- Get all teams route (GET) ---
@team_bp.route('/api/teams', methods=['GET'])
def get_teams():
    teams = list(team_collection.find({}, {'_id': 0, 'team_name': 1}))
    return jsonify({'teams': teams})

# --- Get note by header (POST) ---
@note_bp.route('/api/note', methods=['POST'])
def get_note():
    data = request.get_json()
    header = data.get('Header')
    if not header:
        return jsonify({'error': 'Header is required'}), 400
    note = note_collection.find_one({'Header': header}, {'_id': 0})
    if note:
        return jsonify(note)
    else:
        return jsonify({'error': 'Note not found'}), 404


