from flask import Blueprint, jsonify ,request
from db.connect import user_collection

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/user', methods=['GET'])
def get_user():
    document = user_collection.find_one()
    if document and "username" in document:
        return jsonify({"username": document["username"]})
    else:
        return jsonify({"error": "No user found or 'username' field missing."}), 404


@user_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = user_collection.find_one({'username': username, 'password': password})
    if user:
        return jsonify({'message': 'Login successful', 'username': user['username']})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
    

@user_bp.route('/api/signup', methods =['POST'])
def signup():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    fname = data.get('fname')
    lname = data.get('lname')
    email = data.get('email')
    dob = data.get('dob')         # Expecting string (e.g. 'YYYY-MM-DD')
    create_at = data.get('create_at')  # Optional, if not provided will set now

    # Basic required field check
    if not username or not password or not email:
        return jsonify({'error': 'Username, password, and email are required'}), 400

    # Check if username already exists
    existing_user = user_collection.find_one({'username': username})
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 409

    # Optional: parse dob string to date object
    dob_date = None
    if dob:
        try:
            dob_date = datetime.strptime(dob, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'DOB must be in YYYY-MM-DD format'}), 400

    # Set create_at to now if not provided or invalid
    if create_at:
        try:
            create_at_date = datetime.strptime(create_at, '%Y-%m-%dT%H:%M:%S')
        except Exception:
            create_at_date = datetime.utcnow()
    else:
        create_at_date = datetime.utcnow()

    # Insert new user (plaintext password - for demo only)
    new_user = {
        'username': username,
        'password': password,   # WARNING: Store hashed passwords in real app!
        'first_name': fname,
        'last_name': lname,
        'email': email,
        'dob': dob_date,
        'create_at': create_at_date,
    }

    user_collection.insert_one(new_user)

    return jsonify({'message': 'User created successfully', 'username': username}), 201