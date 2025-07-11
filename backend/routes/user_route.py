from flask import Blueprint, jsonify, request
from datetime import datetime
from db.connect import user_collection
import bcrypt

user_bp = Blueprint('user', __name__)

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
        return jsonify({'message': 'Login successful', 'username': user['username']})
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
