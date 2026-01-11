import os
import json
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from src.utils.auth import Auth
from src.utils.write_file import write_file

auth_bp = Blueprint('auth', __name__)
USERS_FILE = os.path.join(os.getcwd(), 'data', 'users.json')

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    # Ensure data directory exists
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@auth_bp.route('/api/v1/auth/register', methods=['POST'])
def register():
    data = request.get_json(silent=True)
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password required"}), 400
    
    username = data['username']
    password = data['password']
    
    users = load_users()
    
    if username in users:
        return jsonify({"error": "User already exists"}), 409
        
    users[username] = generate_password_hash(password)
    save_users(users)
    
    return jsonify({"message": f"User {username} registered successfully"}), 201

@auth_bp.route('/api/v1/auth/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password required"}), 400

    username = data['username']
    password = data['password']
    
    users = load_users()
    
    if username not in users or not check_password_hash(users[username], password):
        return jsonify({"error": "Invalid credentials"}), 401
        
    auth = Auth()
    token = auth.generate_token(username)
    
    return jsonify({
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": auth.expiration_delta
    }), 200

@auth_bp.route('/api/v1/auth/refresh', methods=['POST'])
@Auth.login_required
def refresh():
    # In a real scenario, this would check a refresh token. 
    # For now, we just issue a new access token if the current one is valid (checked by decorator).
    # Since we can't easily extract identity from decorator in this simple setup without modifying Auth,
    # we will rely on client re-authenticating or improving Auth class later.
    # For this implementation, we'll return a stub.
    return jsonify({"message": "Refresh endpoint implemented (stub). Re-login required."}), 200
