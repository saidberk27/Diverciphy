import os
from datetime import datetime
from flask import Flask, request, jsonify
from src.utils.read_file import read_file
from src.utils.get_latest_file_from_dir import get_latest_file 
from dotenv import load_dotenv
import requests

app = Flask(__name__) #TODO: Create global architecture for app object.

@app.route('/send_shard', methods=['GET', 'POST'])
def send_shard():
    load_dotenv()
    machine_type = os.getenv("MACHINE_TYPE", "")

    match machine_type:
        case "MASTER":
            shard = read_file('../../shards/recieved_shard/recieved_shard.pem')

        case "WORKER":
            shard = get_latest_file('../../shards/recieved_shards/', file_extension='shard_*.pem')

        case _:
            return jsonify({"error": "MACHINE_TYPE is not set properly."}), 500
   
    if not shard:
        return jsonify({"error": "Shard could not be read!"}), 500

    timestamp = datetime.utcnow().isoformat()

    if request.method == 'GET':
        return jsonify({"shard": shard, "timestamp": timestamp}), 200

    if request.method == 'POST':
        data = request.get_json()
        
        target_address = data.get('address')
        if not target_address:
            return jsonify({"error": "Missing 'address' key in JSON body!"}), 400

        try:
            response = requests.post(target_address, json={"shard": shard, "timestamp": timestamp}, timeout=5)
            
            return jsonify({
                "status": "success",
                "address": target_address,
                "timestamp": timestamp,
                "remote_response": response.json()
            }), response.status_code

        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Failed to send request: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)