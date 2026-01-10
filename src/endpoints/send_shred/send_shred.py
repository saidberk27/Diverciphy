import os
from datetime import datetime
from flask import Flask, request, jsonify
from src.utils.read_file import read_file
from src.utils.get_latest_file_from_dir import get_latest_file 
from src.utils.auth import Auth
from dotenv import load_dotenv
import requests

app = Flask(__name__) #TODO: Create global architecture for app object.

# @Auth.login_required
def send_shred():
    load_dotenv()
    machine_type = os.getenv("MACHINE_TYPE", "")

    if machine_type == "MASTER":
        shred_path = 'src/shreds/generated_shreds/generated_shred.pem'

    elif machine_type == "WORKER":
        shred_path = get_latest_file('src/shreds/recieved_shreds', file_extension='*.pem')
        shred = read_file(shred_path)
        worker_index = os.getenv("WORKER_INDEX", "0") 
    else:
        return jsonify({"error": "MACHINE_TYPE is not set properly."}), 500
   
    if not shred:
        return jsonify({"error": "shred could not be read!"}), 500

    timestamp = datetime.utcnow().isoformat()

    if request.method == 'GET':
        return jsonify({"shred": shred, "timestamp": timestamp}), 200

    if request.method == 'POST':
        data = request.get_json()
        
        target_address = data.get('address')
        if not target_address:
            return jsonify({"error": "Missing 'address' key in JSON body!"}), 400

        try:
            auth = Auth()
            token = auth.generate_token(identity="SourceNode")
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Distributor-Index": str(worker_index) 
            }

            payload = {"shred": shred, "timestamp": timestamp}
            
            response = requests.post(target_address, json=payload, headers=headers, timeout=5)
            
            return jsonify({
                "status": "sent",
                "index_sent": worker_index,
                "remote_response": response.json() if response.status_code == 200 else "Error"
            }), response.status_code

        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Failed to send request: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)