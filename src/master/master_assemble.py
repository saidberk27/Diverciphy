import os
import json
import requests
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from datetime import datetime

# Importing the Core class
from src.core.assemble import Assemble 

# Helper for timestamp consistency
def is_timestamp_consistent(timestamps, tolerance=5.0):
    """
    Checks if timestamps are consistent within a tolerance (in seconds).
    """
    if not timestamps: return False
    avg = sum(timestamps) / len(timestamps)
    return all(abs(t - avg) <= tolerance for t in timestamps)

class MasterAssembleEndpoint:
    def __init__(self, app: Flask):
        self.app = app
        load_dotenv()
        
        self.worker_addresses = json.loads(os.getenv("ASSEMBLER_ADRESSES", '["http://localhost:5001", "http://localhost:5002"]'))
        self.file_password = os.getenv("FILE_PASSWORD", "supersecretpassword")
        
        self.assembler = Assemble()
        
        self.last_assembled_data = None 
        
        # --- Register Routes ---
        self._register_routes()
        print(f"[Master] Initialized. Worker Addresses: {self.worker_addresses}")

    def parse_timestamp(self, ts_string):
        """
        Parses a date string into a Unix timestamp (float).
        Handles extra quotes and ISO formats.
        """
        try:
            # FIX: Remove whitespace AND surrounding quotes that might come from JSON
            clean_ts = ts_string.strip().strip('"').strip("'")
    
            try:
                dt_object = datetime.fromisoformat(clean_ts)
            except ValueError:
                dt_object = datetime.strptime(clean_ts, "%Y-%m-%d %H:%M:%S")
            
            return dt_object.timestamp()
            
        except Exception as e:
            print(f"[Master Error] Could not parse timestamp '{ts_string}': {e}")
            return None

    def check_worker_health(self):
        """Checks if all workers are reachable."""
        status_report = {}
        for addr in self.worker_addresses:
            try:
                resp = requests.get(f"{addr}/health", timeout=2)
                status_report[addr] = "Healthy" if resp.status_code == 200 else f"Error: {resp.status_code}"
            except Exception as e:
                status_report[addr] = f"Unreachable: {str(e)}"
        return jsonify(status_report)

    def get_metadata(self):
        """Mock Metadata Service"""
        return list(range(len(self.worker_addresses)))

    def collect_received_shreds_internal(self):
        """
        Iterates through workers and collects shreds.
        """
        shreds = {} 
        
        for index, addr in enumerate(self.worker_addresses):
            try:
                print(f"[Master] Requesting: {addr}/send_shred")
                response = requests.get(f"{addr}/send_shred", timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    shred_content = data.get("shred", "")
                    
                    if "," in shred_content:
                        parts = shred_content.split(",", 1)
                        ts_str = parts[0]
                        val = parts[1].encode('utf-8') 
                        
                        # Parse timestamp with the new robust function
                        ts = self.parse_timestamp(ts_str)
                        
                        if ts is None:
                            print(f"[Master Error] Skipping invalid timestamp from {addr}")
                            continue

                        idx = int(response.headers.get("Distributor-Index", index))
                        shreds[idx] = (val, ts)
                        print(f"[Master] Shred collected from {addr} (Index: {idx}, Time: {ts})")
                    else:
                        print(f"[Master Error] {addr} returned invalid format.")
                else:
                    print(f"[Master Error] {addr} status: {response.status_code}")
            except Exception as e:
                print(f"[Master Error] {addr} unreachable: {e}")
                
        return shreds

    def assemble_shreds_handler(self):
        metadata = self.get_metadata()
        collected_shreds = self.collect_received_shreds_internal()
        
        if len(collected_shreds) < len(metadata):
            return jsonify({
                "status": "fail",
                "message": f"Missing parts. Expected: {len(metadata)}, Received: {len(collected_shreds)}"
            }), 400

        assembled_data = b""
        timestamps = []

        try:
            for part_index in metadata:
                if part_index not in collected_shreds:
                     return jsonify({"status": "fail", "message": f"Index {part_index} missing."}), 400
                
                data_part, ts = collected_shreds[part_index]
                assembled_data += data_part
                timestamps.append(ts)
            
            if not is_timestamp_consistent(timestamps):
                return jsonify({
                    "status": "acid_fail", 
                    "message": "Timestamps are inconsistent! Data integrity compromised."
                }), 409

            self.last_assembled_data = assembled_data
            return jsonify({
                "status": "success",
                "message": "Data assembled successfully.",
                "size": len(assembled_data)
            }), 200

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    def decrypt_data_handler(self):
        if self.last_assembled_data is None:
            return jsonify({"status": "fail", "message": "Run assemble process first."}), 400
        
        decrypted = self.assembler.decrypt_data(self.last_assembled_data, self.file_password)
        
        if decrypted:
            try:
                return jsonify({"status": "success", "data": decrypted.decode('utf-8')}), 200
            except:
                return jsonify({"status": "success", "data_hex": decrypted.hex()}), 200
        else:
            return jsonify({"status": "fail", "message": "Decryption failed (Wrong Key/Password)."}), 403

    def auto_process_handler(self):
        print("[Master] Starting AUTO process...")
        assemble_response, status_code = self.assemble_shreds_handler()
        
        # Check if assembly failed
        if status_code != 200:
            print(f"[Master] Auto: Assembly failed ({status_code})")
            return assemble_response, status_code

        # Proceed to decryption
        return self.decrypt_data_handler()

    def generate_keys_handler(self):
        try:
            self.assembler.generate_and_save_keys(self.file_password)
            return jsonify({"status": "success", "message": "New keys generated."}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    def _register_routes(self):
        self.app.add_url_rule('/assemble_shreds', view_func=self.assemble_shreds_handler, methods=['POST'])
        self.app.add_url_rule('/decrypt_data', view_func=self.decrypt_data_handler, methods=['POST'])
        self.app.add_url_rule('/auto', view_func=self.auto_process_handler, methods=['POST', 'GET'])
        self.app.add_url_rule('/health', view_func=lambda: jsonify({"status": "Master Healthy"}), methods=['GET'])
        self.app.add_url_rule('/check_workers', view_func=self.check_worker_health, methods=['GET'])
        self.app.add_url_rule('/generate_keys', view_func=self.generate_keys_handler, methods=['POST'])

    def run(self, debug=True, port=5555):
        self.app.run(host='0.0.0.0', debug=debug, port=port)

if __name__ == '__main__':
    app = Flask(__name__)
    master_node = MasterAssembleEndpoint(app)
    master_node.run(port=5556)