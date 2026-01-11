import os
import base64 
from datetime import datetime
from flask import Flask, request, jsonify
from src.utils.read_file import read_file
from src.utils.get_latest_file_from_dir import get_latest_file 
from src.utils.auth import Auth
from dotenv import load_dotenv
import requests

app = Flask(__name__)

# @Auth.login_required
def send_shred():
    load_dotenv()
    machine_type = os.getenv("MACHINE_TYPE", "")
    
    shred_bytes = None 
    

    if machine_type == "MASTER":
        shred_path = 'src/shreds/generated_shreds/generated_shred.pem'
        shred_bytes = read_file(shred_path)
        print(shred_bytes)
        
    elif machine_type == "WORKER":
        worker_index = int(os.getenv("WORKER_INDEX", "0"))             
        base_path = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))
            
        shred_filename = f'shred_{worker_index + 1}.pem'
        shred_path = os.path.join(base_path, 'src', 'shreds', 'recieved_shreds', shred_filename)            
        print(f"[DEBUG] Reading shred from: {shred_path}")
            
        shred_bytes = read_file(shred_path)

    else:
        print(e)
        return jsonify({"error": "MACHINE_TYPE is not set properly."}), 500
   
    if not shred_bytes:
        print("Shred could not be read")
        return jsonify({"error": "shred could not be read!"}), 500

    shred_str = base64.b64encode(shred_bytes).decode('utf-8')

    timestamp = datetime.utcnow().isoformat()

    if request.method == 'GET':
        return jsonify({"shred": shred_str, "timestamp": timestamp}), 200

    if request.method == 'POST':
        data = request.get_json()
        
        target_address = data.get('address')
        if not target_address:
            return jsonify({"error": "Missing 'address' key in JSON body!"}), 400

        try:
            auth = Auth()
            token = auth.generate_token(identity="SourceNode")
            current_index = os.getenv("WORKER_INDEX", "0") 

            headers = {
                "Authorization": f"Bearer {token}",
                "Distributor-Index": str(current_index) 
            }

            payload = {"shred": shred_str, "timestamp": timestamp}
            
            response = requests.post(target_address, json=payload, headers=headers, timeout=5)
            
            return jsonify({
                "status": "sent",
                "index_sent": current_index,
                "remote_response": response.json() if response.status_code == 200 else "Error"
            }), response.status_code

        except requests.exceptions.RequestException as e:
            print(e)
            return jsonify({"error": f"Failed to send request: {str(e)}"}), 500