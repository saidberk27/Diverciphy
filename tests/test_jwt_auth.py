import unittest
import os
import sys
import time
import jwt
import json
from flask import Flask

# Add project root to path to ensure imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.auth import Auth
from src.endpoints.recieve_shred.recieve_shred import app as recieve_app
from src.endpoints.send_shred.send_shred import app as send_app

class TestJWTAuth(unittest.TestCase):
    def setUp(self):
        # Set up test environment variables
        os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
        os.environ['JWT_EXPIRATION_DELTA'] = '2' # 2 seconds for expiration test
        self.auth = Auth()
        
        # Setup Flask Test Clients
        self.recieve_client = recieve_app.test_client()
        self.send_client = send_app.test_client()
        
        recieve_app.config['TESTING'] = True
        send_app.config['TESTING'] = True

    def test_01_token_generation(self):
        """Test if token is generated correctly and contains correct identity."""
        identity = "TestUser"
        token = self.auth.generate_token(identity)
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)
        
        # Decode without verification to check payload
        decoded = jwt.decode(token, options={"verify_signature": False})
        self.assertEqual(decoded['sub'], identity)

    def test_02_token_verification_success(self):
        """Test if a valid token is successfully verified."""
        token = self.auth.generate_token("ValidUser")
        decoded = self.auth.verify_token(token)
        self.assertEqual(decoded['sub'], "ValidUser")

    def test_03_token_expiration(self):
        """Test if expired token raises an exception."""
        # Set very short expiration
        os.environ['JWT_EXPIRATION_DELTA'] = '1'
        short_lived_auth = Auth()
        token = short_lived_auth.generate_token("QuickUser")
        
        # Wait for expiration
        time.sleep(1.5)
        
        with self.assertRaises(Exception) as context:
            short_lived_auth.verify_token(token)
        self.assertIn("Token has expired", str(context.exception))

    def test_04_invalid_token_signature(self):
        """Test if token signed with wrong key is rejected."""
        # Generate token with different key
        payload = {"sub": "Hacker"}
        fake_token = jwt.encode(payload, "wrong-key", algorithm="HS256")
        
        with self.assertRaises(Exception) as context:
            self.auth.verify_token(fake_token)
        self.assertIn("Invalid token", str(context.exception))

    def test_05_recieve_shred_access_denied(self):
        """Endpoint Protection: Access /recieve_shred without token."""
        response = self.recieve_client.post('/recieve_shred', json={})
        self.assertEqual(response.status_code, 401)
        self.assertIn(b"Authentication Token is missing", response.data)

    def test_06_recieve_shred_access_granted(self):
        """Endpoint Protection: Access /recieve_shred with valid token."""
        token = self.auth.generate_token("SourceNode")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Content validation will fail (400) but Auth should pass (not 401)
        response = self.recieve_client.post('/recieve_shred', 
                                          json={"shred": "data", "timestamp": "now"}, 
                                          headers=headers)
        
        # If 400 or 200, it means Auth passed. If 401, Auth failed.
        self.assertNotEqual(response.status_code, 401, "Auth failed on valid token")

    def test_07_send_shred_access_denied(self):
        """Endpoint Protection: Access /send_shred without token."""
        response = self.send_client.get('/send_shred')
        self.assertEqual(response.status_code, 401)

    def test_08_send_shred_access_granted(self):
        """Endpoint Protection: Access /send_shred with valid token."""
        token = self.auth.generate_token("AssemblerNode")
        headers = {"Authorization": f"Bearer {token}"}
        
        # We expect 500 because we didn't mock file reading, but NOT 401
        response = self.send_client.get('/send_shred', headers=headers)
        self.assertNotEqual(response.status_code, 401, "Auth failed on valid token")

if __name__ == '__main__':
    unittest.main()
