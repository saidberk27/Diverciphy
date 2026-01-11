
import unittest
import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

from src.master.master_shred import app as master_shred_app
from src.master.master_shred import MasterShredEndpoint

class TestEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        master_shred_app.config['TESTING'] = True
        # Initialize the endpoints to register routes
        cls.endpoint = MasterShredEndpoint(master_shred_app)
        cls.client = master_shred_app.test_client()

    def test_auth_flow(self):
        # 1. Register
        username = "test_user_unit"
        password = "password123"
        
        # Check if user exists (might be from previous run), if so, ignore 409
        resp = self.client.post('/api/v1/auth/register', json={"username": username, "password": password})
        if resp.status_code != 409:
            self.assertEqual(resp.status_code, 201)
        
        # 2. Login
        resp = self.client.post('/api/v1/auth/login', json={"username": username, "password": password})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("access_token", data)
        
        token = data['access_token']
        
        # 3. Test Refresh
        resp = self.client.post('/api/v1/auth/refresh', headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resp.status_code, 200)

    def test_nodes_endpoint(self):
        resp = self.client.get('/api/v1/nodes')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("nodes", data)
        self.assertIsInstance(data['nodes'], list)

    def test_analytics_endpoints(self):
        resp = self.client.get('/api/v1/analytics/paths')
        self.assertEqual(resp.status_code, 200)
        self.assertIn("data", resp.get_json())
        
        resp = self.client.get('/api/v1/analytics/threats')
        self.assertEqual(resp.status_code, 200)
        self.assertIn("logs", resp.get_json())

if __name__ == '__main__':
    unittest.main()
