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
    
