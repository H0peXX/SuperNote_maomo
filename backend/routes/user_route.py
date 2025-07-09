from flask import Blueprint, jsonify
from db.connect import user_collection

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/user', methods=['GET'])
def get_user():
    document = user_collection.find_one()
    if document and "username" in document:
        return jsonify({"username": document["username"]})
    else:
        return jsonify({"error": "No user found or 'username' field missing."}), 404
