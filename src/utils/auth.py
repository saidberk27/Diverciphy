import jwt
import os
import datetime
from functools import wraps
from flask import request, jsonify

class Auth:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY")
        self.expiration_delta = int(os.getenv("JWT_EXPIRATION_DELTA", 30))
        
        if not self.secret_key:
            raise ValueError("JWT_SECRET_KEY environment variable is not set.")

    def generate_token(self, identity: str) -> str:
        """
        Generates a JWT token with a short expiration time.
        """
        payload = {
            "sub": identity,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=self.expiration_delta),
            "iat": datetime.datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def verify_token(self, token: str):
        """
        Verifies the JWT token. Returns payload if valid, raises error otherwise.
        """
        try:
            return jwt.decode(token, self.secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")

    @staticmethod
    def login_required(f):
        """
        Flask decorator to protect endpoints.
        """
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            
            # Check Authorization header (Bearer <token>)
            if "Authorization" in request.headers:
                auth_header = request.headers["Authorization"]
                if auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]
            
            if not token:
                return jsonify({"error": "Authentication Token is missing!"}), 401
            
            try:
                # Instantiate Auth inside the request to ensure env vars are loaded
                auth = Auth()
                auth.verify_token(token)
            except Exception as e:
                return jsonify({"error": str(e)}), 401
                
            return f(*args, **kwargs)
        
        return decorated
