import os
import json
import requests
import datetime
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import base64
# Import Logic Layer
from src.core.shred import Shred

class MasterShredEndpoint:
    def __init__(self, app: Flask):
        self.app = app
        load_dotenv()
        
        self.worker_addresses = json.loads(os.getenv("SHREDDER_ADRESSES", '[]'))
        
        self.master_assembler_url = os.getenv("MASTER_ASSEMBLER_URL", "")
        
        self.shredder = Shred()
        
        self._register_routes()
        print(f"[Master Shredder] Initialized. Target Workers: {len(self.worker_addresses)}")

    def check_worker_health(self):
        """Checks if target worker nodes are reachable."""
        status = {}
        for addr in self.worker_addresses:
            try:
                resp = requests.get(f"{addr}/health", timeout=2)
                status[addr] = "OK" if resp.status_code == 200 else f"Error {resp.status_code}"
            except Exception as e:
                status[addr] = f"Unreachable: {e}"
        return jsonify(status)

    def fetch_public_key(self):
        """
        Fetches the Public Key from the Master Assembler Node.
        """
        try:
            print(f"[Master Shredder] Fetching key from {self.master_assembler_url}...")
            resp = requests.get(f"{self.master_assembler_url}/send_public_key", timeout=3)
            
            if resp.status_code == 200:
                key_data = resp.content
                if self.shredder.load_public_key_from_bytes(key_data):
                    return True, "Key loaded successfully."
                else:
                    return False, "Failed to load key in Core."
            else:
                return False, f"Assembler returned status {resp.status_code}"
        except Exception as e:
            return False, f"Network Error: {e}"

    def distribute_shreds(self, shreds, timestamp_str):
        """
        Sends the shredded chunks to the worker nodes.
        shreds: List of (original_index, data_bytes)
        """
        if len(shreds) > len(self.worker_addresses):
            print("[Master Shredder Error] More shreds than workers! Resize required.")
            return False

        results = {}
        
        for i, (original_index, data_bytes) in enumerate(shreds):
            target_node = self.worker_addresses[i]

            print(len(data_bytes))
            shred_b64_str = base64.b64encode(data_bytes).decode('utf-8')
            print(len(shred_b64_str))
            payload = {
                "shred": shred_b64_str,
                "timestamp": timestamp_str,
                "original_index": original_index
            }
            
            try:
                resp = requests.post(f"{target_node}/recieve_shred", json=payload, timeout=3)
                if resp.status_code == 200:
                    results[target_node] = "Sent"
                    print(f"[Master Shredder] Shred {original_index} sent to {target_node}")
                else:
                    results[target_node] = f"Failed {resp.status_code}"
                    print(f"Failed {resp.status_code}")
            except Exception as e:
                results[target_node] = f"Error {e}"
                
        return results

    def auto_process(self):
        """
        Endpoint: /auto
        Full Workflow: Fetch Key -> Encrypt -> Shred -> Distribute
        """
        user_input = request.json.get("payload")
        if not user_input:
            return jsonify({"status": "fail", "message": "No payload provided."}), 400

        print("[Master Shredder] Starting AUTO process...")

        success, msg = self.fetch_public_key()
        if not success:
            return jsonify({"status": "fail", "message": f"Key Fetch Error: {msg}"}), 502

        encrypted_data = self.shredder.encrypt_payload(user_input)
        
        if not encrypted_data:
            return jsonify({"status": "fail", "message": "Encryption failed."}), 500

        num_parts = len(self.worker_addresses)
        if num_parts == 0:
             return jsonify({"status": "fail", "message": "No workers defined."}), 500
             
        shreds, encrypted_metadata = self.shredder.shred_data(encrypted_data, num_parts)

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        distribution_report = self.distribute_shreds(shreds, current_time)

        return jsonify({
            "status": "success",
            "timestamp": current_time,
            "distribution_report": distribution_report,
            "metadata_hex": encrypted_metadata.hex()
        }), 200

    def _register_routes(self):
        self.app.add_url_rule('/auto', view_func=self.auto_process, methods=['POST'])
        self.app.add_url_rule('/check_workers', view_func=self.check_worker_health, methods=['GET'])
        self.app.add_url_rule('/health', view_func=lambda: jsonify({"status": "Shredder Healthy"}), methods=['GET'])

    def run(self, debug=True, port=6000):
        print("[Master Shredder] Running...")
        self.app.run(host='0.0.0.0', debug=debug, port=port)

if __name__ == '__main__':
    app = Flask(__name__)
    shredder_node = MasterShredEndpoint(app)
    shredder_node.run(port=6000)