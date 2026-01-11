import os
import json
import requests
from flask import Flask, jsonify, request, Response
from dotenv import load_dotenv
from datetime import datetime
import base64

# Importing the Core class
from src.core.assemble import Assemble 

# Helper for timestamp consistency
def is_timestamp_consistent(timestamps, tolerance=5.0):
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
        """Parses a date string into a Unix timestamp (float)."""
        try:
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
        return list(range(len(self.worker_addresses)))

    def collect_received_shreds_internal(self):
        shreds = {} 
        for index, addr in enumerate(self.worker_addresses):
            try:
                print(f"[Master] Requesting: {addr}/send_shred")
                response = requests.get(f"{addr}/send_shred", timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    shred_b64 = data.get("shred")      
                    ts_str = data.get("timestamp")     
                    
                    if shred_b64 and ts_str:
                        try:
                            shred_val = base64.b64decode(shred_b64)
                            
        
                            ts = self.parse_timestamp(ts_str)
                            
                            if ts is None: 
                                print(f"[Master Error] Invalid timestamp from {addr}")
                                continue

                            idx = int(response.headers.get("Distributor-Index", index))
                            
                            # Veriyi (bytes) ve zamanı kaydet
                            shreds[idx] = (shred_val, ts)
                            print(f"[Master] Received shred from worker {idx}")
                            
                        except Exception as e:
                            print(f"[Master Error] Decoding failed for {addr}: {e}")
                    else:
                        print(f"[Master Error] {addr} returned missing data fields.")
                        

                else:
                    print(f"[Master Error] {addr} status: {response.status_code}")
            
            except requests.exceptions.RequestException as e:
                print(f"[Master Error] Request failed for {addr}: {e}")
                
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
                print(data_part)
                assembled_data += data_part
                timestamps.append(ts)
            
            if not is_timestamp_consistent(timestamps):
                return jsonify({"status": "acid_fail", "message": "Timestamps inconsistent!"}), 409

            self.last_assembled_data = assembled_data
            return jsonify({"status": "success", "message": "Assembled successfully.", "size": len(assembled_data)}), 200

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    def decrypt_data_handler(self):
        if self.last_assembled_data is None:
            return jsonify({"status": "fail", "message": "Run assemble first."}), 400
        decrypted = self.assembler.decrypt_data(self.last_assembled_data, self.file_password)
        
        if decrypted:
            try:
                return jsonify({"status": "success", "data": decrypted.decode('utf-8')}), 200
            except:
                return jsonify({"status": "success", "data_hex": decrypted.hex()}), 200
        else:
            return jsonify({"status": "fail", "message": "Decryption failed."}), 403

    def send_public_key_handler(self):
        """
        API Endpoint: /send_public_key
        Reads the public key from Core and sends it to the requester.
        """
        key_bytes = self.assembler.get_public_key_bytes()
        
        if key_bytes:
            return Response(key_bytes, mimetype='application/x-pem-file', status=200)
        else:
            return jsonify({"status": "fail", "message": "Public key not found. Run /generate_keys first."}), 404

    def auto_process_handler(self):
        assemble_response, status_code = self.assemble_shreds_handler()
        if status_code != 200: return assemble_response, status_code
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

        self.app.add_url_rule('/send_public_key', view_func=self.send_public_key_handler, methods=['GET'])
        
        self.app.add_url_rule('/health', view_func=lambda: jsonify({"status": "Master Healthy"}), methods=['GET'])
        self.app.add_url_rule('/check_workers', view_func=self.check_worker_health, methods=['GET'])
        self.app.add_url_rule('/generate_keys', view_func=self.generate_keys_handler, methods=['POST'])

    def run(self, debug=True, port=5556):
        self.app.run(host='0.0.0.0', debug=debug, port=port)

if __name__ == '__main__':
    app = Flask(__name__)
    master_node = MasterAssembleEndpoint(app)
    master_node.run(port=5556)